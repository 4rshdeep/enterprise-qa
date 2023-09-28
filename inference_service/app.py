import os
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from utils import create_completion
import requests
from fastapi import HTTPException


app = FastAPI()


class InferenceRequest(BaseModel):
    context: str
    query: str
    prompt: str
    user_details: str
    answer_generation_prompt: str
    retry: Optional[bool] = None
    retry_prompt: Optional[str] = None
    num_retries: Optional[int] = None
    debug: bool = False


class InferenceResponse(BaseModel):
    answer: Optional[str] = None
    explanation: str
    error: bool = False


# this is created to parse llm response as a json
class ValidSQL(BaseModel):
    can_be_answered: bool = Field(
        description="Boolean to indicate whether the question can be answered or not"
    )
    sql_query: str = Field(description="This contains the valid SQLite query to be run")
    explanation: str = Field(
        description="Valid explanation for the SQLite query or why the question cannot be answered"
    )


class ValidAnswer(BaseModel):
    answer: str = Field(
        description="This answers the question by using the results of the SQL Query"
    )
    explanation: str = Field(
        description="This explains how the result was achieved by explaining the SQL Query"
    )


def run_query(query: str):
    # URL of the Query Engine service
    query_engine_url = f"http://query-engine:{os.getenv('QUERY_SERVICE_PORT')}"

    try:
        # Make a POST request to the Query Engine service
        response = requests.post(
            f"{query_engine_url}/execute_query/", json={"query": query}
        )

        # Raise an HTTPException if the response status code is not successful
        response.raise_for_status()

        # convert result in JSON format
        result = response.json()

        return result

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors and raise an HTTPException with the status code and detail message
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HTTP error occurred: {str(e)}",
        )
    except Exception as e:
        # Handle other exceptions if necessary
        raise e


def create_completion_dummy():
    # Creating an instance of ValidSQL
    valid_sql_instance = ValidSQL(
        can_be_answered=True,
        sql_query='SELECT COUNT(*) AS num_employees FROM "Employee";',
        explanation="The SQL query COUNT(*) is used to count the number of rows in the 'Employee' table, which gives us the total number of employees.",
    )
    return valid_sql_instance


def perform_inference(formatted_prompt: str) -> ValidSQL:
    # get inference with the required format
    if DEBUG:
        return create_completion_dummy()

    messages = [{"role": "user", "content": formatted_prompt}]
    result = create_completion(messages, ValidSQL, model="gpt-4")

    return result


def get_answer_explanation(prompt: str) -> ValidAnswer:
    if DEBUG:
        valid_answer_instance = ValidAnswer(
            answer="Number of employees are 8",
            explanation="The SQL query COUNT(*) is used to count the number of rows in the 'Employee' table, which gives us the total number of employees.",
        )
        return valid_answer_instance

    messages = [{"role": "user", "content": prompt}]
    result = create_completion(messages, ValidAnswer, model="gpt-4")

    return result


@app.post("/infer/", response_model=InferenceResponse)
async def inference(request: InferenceRequest):
    global DEBUG
    prompt = request.prompt
    query = request.query
    context = request.context
    retry = request.retry
    retry_prompt = request.retry_prompt
    user_details = request.user_details
    num_retries = request.num_retries
    answer_generation_prompt = request.answer_generation_prompt
    DEBUG = request.debug

    formatted_prompt = prompt.format(
        query=query, context=context, user_details=user_details
    )

    result = perform_inference(formatted_prompt)

    if not result.can_be_answered:
        return {"answer": None, "explanation": result.explanation}

    query_result = run_query(result.sql_query)

    if query_result.get("result"):
        # given question, sql, sql response - generate answer to the question
        formatted_prompt = answer_generation_prompt.format(
            user_details=user_details,
            question=request.query,
            query=result.sql_query,
            explanation=result.explanation,
            result=query_result.get("result"),
        )

        answer = get_answer_explanation(formatted_prompt)
        return {"answer": answer.answer, "explanation": answer.explanation}

    if retry:
        for i in range(num_retries):
            error = query_result.error
            old_query = result.query
            formatted_retry_prompt = retry_prompt.format(
                query=query,
                context=context,
                user_details=user_details,
                error=error,
                sql_query=old_query,
            )
            result = perform_inference(formatted_retry_prompt)
            query_result = run_query(result.query)

            if not query_result.error:
                break

        if query_result.result:
            # given question, sql, sql response - generate answer to the question
            formatted_prompt = answer_generation_prompt.format(
                user_details=user_details,
                question=request.query,
                query=result.sql_query,
                explanation=result.explanation,
                result=query_result.get("result"),
            )

            answer = get_answer_explanation(formatted_prompt)
            return {"answer": answer.answer, "explanation": answer.explanation}

    return {
        "error": True,
        "answer": "Can you rephrase your question?",
        "explanation": "Could not find a way to answer that",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=int(os.getenv("INFERENCE_SERVICE_PORT", "8002"))
    )

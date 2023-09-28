import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

import requests


# Create a logger object
logger = logging.getLogger("orchestrator")

# Set the logging level to capture INFO and above
logger.setLevel(logging.INFO)

# Create a console handler and set its level to INFO
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create a formatter and attach it to the console handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

app = FastAPI()

# Define the URLs of the other services
retrieval_service_url = (
    f"http://retrieval-service:{os.getenv('RETRIEVAL_SERVICE_PORT')}"
)
prompt_management_service_url = (
    f"http://prompt-manager:{os.getenv('PROMPT_MANAGEMENT_SERVICE_PORT')}"
)
inference_service_url = (
    f"http://inference-service:{os.getenv('INFERENCE_SERVICE_PORT')}"
)


class OrchestratorRequest(BaseModel):
    query: str


class InferenceServiceResponse(BaseModel):
    answer: str
    explanation: str


class OrchestratorResponse(BaseModel):
    inference_result: InferenceServiceResponse


@app.post("/orchestrate/", response_model=OrchestratorResponse)
async def orchestrate(request: OrchestratorRequest):
    try:
        # Make a request to the retrieval service
        retrieval_response = requests.post(
            f"{retrieval_service_url}/retrieve/", json={"query": request.query}
        )
        retrieval_result = retrieval_response.json()

        # Make a request to the prompt management service
        prompt_management_response = requests.post(
            f"{prompt_management_service_url}/fetch_prompt/",
            json={
                "prompt_keys": [
                    "QUESTION_ANSWERING_PROMPT",
                    "QUESTION_ANSWERING_PROMPT_QUERY_ERROR",
                    "FINAL_ANSWER_PROMPT",
                ]
            },
        )
        prompt_management_result = prompt_management_response.json()

        # Make a request to the inference service
        inference_response = requests.post(
            f"{inference_service_url}/infer/",
            json={
                "query": request.query,
                "prompt": prompt_management_result.get("prompts").get(
                    "QUESTION_ANSWERING_PROMPT"
                ),
                "context": retrieval_result.get("context"),
                "user_details": "User is a technical person, explanation can be a bit technical",
                "retry": True,
                "retry_prompt": prompt_management_result.get("prompts").get(
                    "QUESTION_ANSWERING_PROMPT_QUERY_ERROR"
                ),
                "num_retries": 3,
                "answer_generation_prompt": prompt_management_result.get("prompts").get(
                    "FINAL_ANSWER_PROMPT"
                ),
            },
        )
        inference_result = inference_response.json()

        return {"inference_result": inference_result}

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Service communication error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("ORCHESTRATOR_PORT", 8000)))

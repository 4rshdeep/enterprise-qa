import os
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from prompts import COLUMN_DESCRIPTION_PROMPT, TABLE_DESCRIPTION_PROMPT
from prompts import (
    QUESTION_ANSWERING_PROMPT,
    FINAL_ANSWER_PROMPT,
    QUESTION_ANSWERING_PROMPT_QUERY_ERROR,
    QUESTION_ANSWERING_PROMPT_WITH_MEMORY,
)

app = FastAPI()


class PromptRequest(BaseModel):
    prompt_keys: Optional[list] = None


class PromptResponse(BaseModel):
    prompts: Optional[dict] = None
    error: Optional[str] = None


PROMPTS_MAP = {
    "QUESTION_ANSWERING_PROMPT": QUESTION_ANSWERING_PROMPT,
    "QUESTION_ANSWERING_PROMPT_QUERY_ERROR": QUESTION_ANSWERING_PROMPT_QUERY_ERROR,
    "QUESTION_ANSWERING_PROMPT_WITH_MEMORY": QUESTION_ANSWERING_PROMPT_WITH_MEMORY,
    "TABLE_DESCRIPTION_PROMPT": TABLE_DESCRIPTION_PROMPT,
    "COLUMN_DESCRIPTION_PROMPT": COLUMN_DESCRIPTION_PROMPT,
    "FINAL_ANSWER_PROMPT": FINAL_ANSWER_PROMPT,
}


@app.post("/fetch_prompt/", response_model=PromptResponse)
async def fetch_prompt(request: PromptRequest):
    if request.prompt_keys:
        prompts = {
            key: PROMPTS_MAP[key] for key in request.prompt_keys if key in PROMPTS_MAP
        }

        if len(prompts) > 0:
            return {"prompts": prompts}
        else:
            return {"error": "Couldn't find the prompt in the list of prompts"}
    return {"error": "Didn't specify prompt_key"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PROMPT_MANAGEMENT_SERVICE_PORT", "8001")),
    )

import os
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from retrieval import sample_context

app = FastAPI()


class RetrievalRequest(BaseModel):
    query: str


class RetrievalResponse(BaseModel):
    context: str


@app.post("/retrieve/", response_model=RetrievalResponse)
async def retrieve(query: RetrievalRequest):
    return {"context": sample_context}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=int(os.getenv("RETRIEVAL_SERVICE_PORT", "8004"))
    )

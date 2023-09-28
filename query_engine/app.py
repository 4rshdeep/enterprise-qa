import os
from fastapi import FastAPI, HTTPException, Request

from sqlalchemy import create_engine, text
from sql_database import SQLDatabase
from typing import Optional, Sequence

from pydantic import BaseModel

from sqlalchemy.exc import ProgrammingError, SQLAlchemyError

app = FastAPI()


database = SQLDatabase.from_uri("sqlite:///test.db")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    result: Optional[str] = None
    error: Optional[str] = None


@app.post("/execute_query/", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    try:
        query = request.query
        result = database.run(query)
        return {"result": str(result)}
    except SQLAlchemyError as e:
        return {"error": f"Error: {e}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("QUERY_SERVICE_PORT", "8003")))

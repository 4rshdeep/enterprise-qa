import logging
import os
from pydantic import BaseModel, ValidationError
from typing import List
import openai
import json


openai.api_key = os.getenv("OPENAI_API_KEY")


def create_completion(
    messages: List[dict], model_class: BaseModel, retry=2, temperature=0, **kwargs
) -> BaseModel:
    messages.append(
        {
            "role": "system",
            "content": f"Please respond ONLY with valid json that conforms to this pydantic json_schema: {json.dumps(model_class.model_json_schema())}. Do not include additional text other than the object json as we will load this object with json.loads() and pydantic.",
        }
    )

    last_exception = None
    for i in range(retry + 1):
        response = openai.ChatCompletion.create(
            messages=messages, temperature=temperature, **kwargs
        )
        assistant_message = response["choices"][0]["message"]
        content = assistant_message["content"]
        try:
            json_content = json.loads(content)
        except Exception as e:
            last_exception = e
            error_msg = f"json.loads exception: {e}"
            logging.error(error_msg)
            messages.append(assistant_message)
            messages.append({"role": "system", "content": error_msg})
            continue
        try:
            return model_class(**json_content)
        except ValidationError as e:
            last_exception = e
            error_msg = f"pydantic exception: {e}"
            logging.error(error_msg)
            messages.append(assistant_message)
            messages.append({"role": "system", "content": error_msg})
    raise last_exception

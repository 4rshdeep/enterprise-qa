# Enterprise-qa

To run

```
docker-compose build
docker-compose up

```

Ports for individual services can be specified in .env file.


Query can then be sent to orchestrator which returns back the answer

```
curl --location 'localhost:8000/orchestrate/' \
--header 'Content-Type: application/json' \
--data '{
  "query": "Who is our oldest employee?"
}'
```

Response from the orchestrator

```
{
    "inference_result": {
        "answer": "Our oldest employee is Margaret Park.",
        "explanation": "The SQL query selects the first name and last name from the Employee table, orders the results by the birth date in ascending order, and then limits the result to the first record. This gives us the oldest employee, who is Margaret Park."
    }
}
```

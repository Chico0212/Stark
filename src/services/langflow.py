import requests
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

LANGFLOW_URL = f"http://langflow.ideia.com:8270/api/v1/run/{os.getenv('FLOW_ID')}"


def get_response(data: dict) -> str:
    return data["outputs"][0]["outputs"][0]["results"]["message"]["text"]


def generate_test_case(rules: str):
    print("Gerando casos de teste")
    response = requests.post(
        url=LANGFLOW_URL,
        json={"output_type": "chat", "input_type": "chat", "input_value": rules},
        params={"stream": "false"},
        headers={
            "Content-Type": "application/json",
            "x-api-key": os.getenv("LANGFLOW_API_KEY"),
        },
    )

    if not response.ok:
        return

    return get_response(response.json())


if __name__ == "__main__":
    print(generate_test_case("olá tudo bem?"))

from dotenv import load_dotenv
import os
import base64
import requests
import json

load_dotenv()

def get_token():
    client_id = os.getenv("RTE_CLIENT_ID")
    client_secret = os.getenv("RTE_CLIENT_SECRET")
    credentials = f"{client_id}:{client_secret}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()
    url = "https://digital.iservices.rte-france.com/token/oauth/"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Basic {credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    print(f"Token response: {response.json()}")
    return response.json()["access_token"]

def get_production_data(token):
    url = "https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_production_type"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def save_to_json(data, filename="data/raw_production.json"):
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    token = get_token()
    data = get_production_data(token)
    save_to_json(data)


import requests
import json

with open("project_id.txt", "r") as f:
    project_id = f.read()

gate_id = "G1"

url = f"http://127.0.0.1:8000/projects/{project_id}/approve/{gate_id}"

payload = {
  "approved_by": "user",
  "comments": "Approved by user",
  "approved": True
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)

print(response.status_code)
print(response.json())

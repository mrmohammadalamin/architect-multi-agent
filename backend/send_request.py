
import requests
import json

url = "http://127.0.0.1:8000/projects"

payload = {
  "project_name": "Modern Eco-Friendly Family House",
  "project_type": "residential",
  "client_name": "EcoHome Developers",
  "budget_range": "$750,000 - $1,200,000",
  "location": "London, UK",
  "desired_features": ["Smart Home Tech", "Green Roof", "Open Concept Living", "Large Garden", "Energy-efficient HVAC"],
  "project_description": "Design and build a two-story modern eco-friendly family house with smart home technology, a green roof, and an emphasis on energy efficiency and natural light."
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)

if response.status_code == 201:
    project_id = response.json()["project_id"]
    with open("project_id.txt", "w") as f:
        f.write(project_id)

print(response.status_code)
print(response.json())

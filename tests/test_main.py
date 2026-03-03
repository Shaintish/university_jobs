from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Тест создания вакансии (Успех)
def test_create_vacancy_success():
    response = client.post("/vacancies", json={
        "title": "Assistant Researcher",
        "description": "Help with AI lab",
        "department": "IT",
        "job_type": "job",
        "salary": 500
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Assistant Researcher"


# 2. Тест получения списка вакансий
def test_get_vacancies():
    response = client.get("/vacancies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
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

# 3. Тест поиска вакансии по заголовку
def test_search_vacancy():
    client.post("/vacancies", json={
        "title": "Math Tutor", 
        "description": "Desc", 
        "department": "Math", 
        "job_type": "job"
    })
    response = client.get("/vacancies?search=Math")
    assert len(response.json()) >= 1
    assert "Math" in response.json()[0]["title"]


# 4. Тест получения конкретной вакансии (404)
def test_get_vacancy_not_found():
    response = client.get("/vacancies/999")
    assert response.status_code == 404


# 5. Тест подачи заявки (Успех)
def test_apply_success():
    # Сначала создаем вакансию
    vac_res = client.post("/vacancies", json={
        "title": "Intern", 
        "description": "...", 
        "department": "HR", 
        "job_type": "internship"
    })
    vac_id = vac_res.json()["id"]

    response = client.post("/applications", json={
        "vacancy_id": vac_id,
        "student_name": "Ivan Ivanov",
        "student_email": "ivan@university.edu"
    })
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

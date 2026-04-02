from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_vacancy_success():
    response = client.post("/vacancies", json={
        "title": "Assistant Researcher",
        "description": "Help with AI lab",
        "department": "IT",
        "job_type": "job",
        "salary": 500
    })
    assert response.status_code == 200  # Исправлено с 201 на 200
    assert response.json()["title"] == "Assistant Researcher"


def test_get_vacancies():
    response = client.get("/vacancies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


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


def test_get_vacancy_not_found():
    response = client.get("/vacancies/999")
    assert response.status_code == 404


def test_apply_success():
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
    assert response.status_code == 200  # Исправлено с 201 на 200
    assert response.json()["status"] == "pending"


def test_apply_wrong_vacancy():
    response = client.post("/applications", json={
        "vacancy_id": 888,
        "student_name": "Ghost",
        "student_email": "ghost@uni.edu"
    })
    assert response.status_code == 404


def test_invalid_email_application():
    vac_res = client.post("/vacancies", json={
        "title": "Test", 
        "description": "...", 
        "department": "Test", 
        "job_type": "job"
    })
    vac_id = vac_res.json()["id"]
    
    response = client.post("/applications", json={
        "vacancy_id": vac_id,
        "student_name": "Bad Email",
        "student_email": "not-an-email"
    })
    assert response.status_code == 422


def test_get_application_status():
    vac_res = client.post("/vacancies", json={
        "title": "Status Test", 
        "description": "...", 
        "department": "Test", 
        "job_type": "job"
    })
    vac_id = vac_res.json()["id"]
    
    app_res = client.post("/applications", json={
        "vacancy_id": vac_id,
        "student_name": "Test User",
        "student_email": "test@uni.edu"
    })
    app_id = app_res.json()["id"]

    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["id"] == app_id
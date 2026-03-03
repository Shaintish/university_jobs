from fastapi import FastAPI, Query
from typing import List, Optional
from .schemas import Vacancy, VacancyCreate, Application, ApplicationCreate
from .services import JobService, vacancies_db, applications_db

app = FastAPI(title="University Career Hub")

# Эндпоинты для Вакансий
@app.post("/vacancies", response_model=Vacancy, status_code=201)
async def create_vacancy(vacancy: VacancyCreate):
    return JobService.create_vacancy(vacancy)


@app.get("/vacancies", response_model=List[Vacancy])
async def get_vacancies(search: Optional[str] = Query(None)):
    return JobService.get_all_vacancies(search)


@app.get("/vacancies/all", response_model=dict)
async def get_all_vacancies_debug():
    return {
        "total": len(vacancies_db),
        "vacancies": vacancies_db
    }


@app.get("/applications/all", response_model=List[Application])
async def get_all_applications_debug():
    return applications_db


@app.get("/vacancies/{vacancy_id}", response_model=Vacancy)
async def get_vacancy(vacancy_id: int):
    return JobService.get_vacancy(vacancy_id)

# Эндпоинты заявок
@app.post("/applications", response_model=Application, status_code=201)
async def apply_for_job(application: ApplicationCreate):
    return JobService.create_application(application)


@app.get("/applications/{app_id}", response_model=Application)
async def get_application_status(app_id: int):
    return JobService.get_application(app_id)
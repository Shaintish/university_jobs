from .schemas import VacancyCreate, Vacancy, ApplicationCreate, Application, ApplicationStatus
from fastapi import HTTPException

# Имитация БД
vacancies_db = []
applications_db = []


class JobService:
    @staticmethod
    def create_vacancy(data: VacancyCreate) -> Vacancy:
        new_id = len(vacancies_db) + 1
        vacancy = Vacancy(id=new_id, **data.model_dump())
        vacancies_db.append(vacancy)
        return vacancy

    @staticmethod
    def get_all_vacancies(search: str = None):
        if search:
            return [v for v in vacancies_db if search.lower() in v.title.lower()]
        return vacancies_db
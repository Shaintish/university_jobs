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
    
     @staticmethod
    def get_vacancy(vacancy_id: int) -> Vacancy:
        for v in vacancies_db:
            if v.id == vacancy_id:
                return v
        raise HTTPException(status_code=404, detail="Вакансия не найдена")

    @staticmethod
    def create_application(data: ApplicationCreate) -> Application:
        vacancy = next((v for v in vacancies_db if v.id == data.vacancy_id), None)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Вакансия не существует")

        new_id = len(applications_db) + 1
        application = Application(
            id=new_id,
            status=ApplicationStatus.PENDING,
            **data.model_dump()
        )
        applications_db.append(application)
        return application
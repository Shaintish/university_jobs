from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from .schemas import VacancyCreate, ApplicationCreate
from .services import JobService, vacancies_db, applications_db

app = FastAPI(title="University Career Hub")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    vacancies = JobService.get_all_vacancies()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "vacancies": vacancies}
    )

@app.get("/add-vacancy", response_class=HTMLResponse)
async def add_vacancy_form(request: Request):
    return templates.TemplateResponse(
        "add_vacancy.html", 
        {"request": request}
    )

@app.post("/add-vacancy")
async def create_vacancy(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    department: str = Form(...),
    job_type: str = Form(...),
    salary: Optional[int] = Form(None)
):
    try:
        vacancy_data = VacancyCreate(
            title=title,
            description=description,
            department=department,
            job_type=job_type,
            salary=salary
        )
        JobService.create_vacancy(vacancy_data)
        return templates.TemplateResponse(
            "add_vacancy.html",
            {"request": request, "message": "✅ Вакансия успешно создана!"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "add_vacancy.html",
            {"request": request, "error": str(e)}
        )

@app.get("/apply/{vacancy_id}", response_class=HTMLResponse)
async def apply_form(request: Request, vacancy_id: int):
    try:
        vacancy = JobService.get_vacancy(vacancy_id)
        return templates.TemplateResponse(
            "apply.html",
            {"request": request, "vacancy": vacancy}
        )
    except HTTPException:
        return RedirectResponse(url="/", status_code=303)

@app.post("/apply/{vacancy_id}")
async def submit_application(
    request: Request,
    vacancy_id: int,
    student_name: str = Form(...),
    student_email: str = Form(...)
):
    try:
        application_data = ApplicationCreate(
            vacancy_id=vacancy_id,
            student_name=student_name,
            student_email=student_email
        )
        JobService.create_application(application_data)
        return templates.TemplateResponse(
            "apply.html",
            {
                "request": request, 
                "vacancy": JobService.get_vacancy(vacancy_id),
                "message": "✅ Заявка успешно отправлена!"
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "apply.html",
            {
                "request": request, 
                "vacancy": JobService.get_vacancy(vacancy_id),
                "error": str(e)
            }
        )

# Оставьте ваши API эндпоинты
@app.post("/vacancies")
async def create_vacancy_api(vacancy: VacancyCreate):
    return JobService.create_vacancy(vacancy)

@app.get("/vacancies")
async def get_vacancies_api(search: Optional[str] = None):
    return JobService.get_all_vacancies(search)

@app.get("/vacancies/{vacancy_id}")
async def get_vacancy_api(vacancy_id: int):
    return JobService.get_vacancy(vacancy_id)

@app.post("/applications")
async def create_application_api(application: ApplicationCreate):
    return JobService.create_application(application)

@app.get("/applications/{app_id}")
async def get_application_api(app_id: int):
    return JobService.get_application(app_id)
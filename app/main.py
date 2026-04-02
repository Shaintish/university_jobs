from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, List
from .schemas import Vacancy, VacancyCreate, Application, ApplicationCreate, UserCreate, UserLogin
from .services import JobService, UserService, vacancies_db, applications_db
import uuid

app = FastAPI(title="University Career Hub")
templates = Jinja2Templates(directory="templates")

# Хранилище сессий (в памяти)
sessions = {}

# ========== СТРАНИЦЫ САЙТА ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Проверяем, авторизован ли пользователь
    session_id = request.cookies.get("session_id")
    current_user = None
    if session_id and session_id in sessions:
        current_user = sessions[session_id]
    
    vacancies = JobService.get_all_vacancies()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "vacancies": vacancies, "user": current_user}
    )

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        user = UserService.register(UserCreate(username=username, email=email, password=password))
        # Автоматически входим после регистрации
        session_id = str(uuid.uuid4())
        sessions[session_id] = user
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_id", value=session_id)
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": e.detail}
        )

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        user = UserService.login(username, password)
        session_id = str(uuid.uuid4())
        sessions[session_id] = user
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_id", value=session_id)
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": e.detail}
        )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

@app.get("/my-applications", response_class=HTMLResponse)
async def my_applications(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=303)
    
    current_user = sessions[session_id]
    # Получаем заявки по email пользователя
    user_applications = JobService.get_applications_by_email(current_user.email)
    
    return templates.TemplateResponse(
        "my_applications.html",
        {"request": request, "applications": user_applications, "user": current_user}
    )

@app.get("/add-vacancy", response_class=HTMLResponse)
async def add_vacancy_form(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        "add_vacancy.html", 
        {"request": request, "user": sessions[session_id]}
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
            {"request": request, "message": "✅ Вакансия успешно создана!", "user": None}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "add_vacancy.html",
            {"request": request, "error": str(e), "user": None}
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

# ========== API ЭНДПОИНТЫ (оставляем для совместимости) ==========

@app.post("/vacancies", response_model=Vacancy, status_code=200)
async def create_vacancy_api(vacancy: VacancyCreate):
    return JobService.create_vacancy(vacancy)

@app.get("/vacancies", response_model=List[Vacancy])
async def get_vacancies_api(search: Optional[str] = None):
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
async def get_vacancy_api(vacancy_id: int):
    return JobService.get_vacancy(vacancy_id)

@app.post("/applications", response_model=Application, status_code=200)
async def create_application_api(application: ApplicationCreate):
    return JobService.create_application(application)

@app.get("/applications/{app_id}", response_model=Application)
async def get_application_api(app_id: int):
    return JobService.get_application(app_id)
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import Optional, List
from .schemas import Vacancy, VacancyCreate, Application, ApplicationCreate, UserCreate
from .services import JobService, UserService
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uuid

app = FastAPI(title="University Career Hub")
templates = Jinja2Templates(directory="templates")

# Хранилище сессий (в памяти)
sessions = {}

# ========== ОБРАБОТЧИКИ ОШИБОК ВАЛИДАЦИИ ==========

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Детализированная обработка ошибок валидации"""
    errors = []
    for error in exc.errors():
        # Извлекаем название поля
        if len(error["loc"]) > 1:
            field = ".".join(str(loc) for loc in error["loc"][1:])
        else:
            field = error["loc"][-1]
        
        errors.append({
            "field": field,
            "error": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Ошибка валидации данных",
            "details": errors,
            "message": "Пожалуйста, проверьте правильность заполнения полей"
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Детализированная обработка HTTP ошибок"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# ========== СТРАНИЦЫ САЙТА ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
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
    user_applications = JobService.get_applications_by_email(current_user["email"])
    
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
            title=title.strip(),
            description=description.strip(),
            department=department.strip(),
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
        if not vacancy:
            return RedirectResponse(url="/", status_code=303)
        return templates.TemplateResponse(
            "apply.html",
            {"request": request, "vacancy": vacancy}
        )
    except Exception as e:
        print(f"Ошибка в apply_form: {e}")
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
            student_name=student_name.strip(),
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

# ========== API ЭНДПОИНТЫ ==========

@app.post("/vacancies", response_model=Vacancy, status_code=200)
async def create_vacancy_api(vacancy: VacancyCreate):
    return JobService.create_vacancy(vacancy)

@app.get("/vacancies", response_model=List[Vacancy])
async def get_vacancies_api(search: Optional[str] = None):
    return JobService.get_all_vacancies(search)

@app.get("/vacancies/{vacancy_id}", response_model=Vacancy)
async def get_vacancy_api(vacancy_id: int):
    return JobService.get_vacancy(vacancy_id)

@app.post("/applications", response_model=Application, status_code=200)
async def create_application_api(application: ApplicationCreate):
    return JobService.create_application(application)

@app.get("/applications/{app_id}", response_model=Application)
async def get_application_api(app_id: int):
    return JobService.get_application(app_id)

# ========== ОТЛАДОЧНЫЕ ЭНДПОИНТЫ ==========

@app.get("/vacancies/all")
async def get_all_vacancies_debug():
    return JobService.get_all_vacancies()

@app.get("/applications/all")
async def get_all_applications_debug():
    return JobService.get_all_applications()

# ========== ВХОД ДЛЯ РАБОТОДАТЕЛЯ ==========

@app.get("/employer/login", response_class=HTMLResponse)
async def employer_login_form(request: Request):
    return templates.TemplateResponse("employer_login.html", {"request": request})

@app.post("/employer/login")
async def employer_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == "employer" and password == "admin123":
        session_id = str(uuid.uuid4())
        employer_user = {
            "id": 999, 
            "username": "employer", 
            "email": "employer@company.com", 
            "role": "employer"
        }
        sessions[session_id] = employer_user
        response = RedirectResponse(url="/admin/applications", status_code=303)
        response.set_cookie(key="session_id", value=session_id)
        return response
    else:
        return templates.TemplateResponse(
            "employer_login.html",
            {"request": request, "error": "Неверный логин или пароль"}
        )

# ========== АДМИН-ПАНЕЛЬ РАБОТОДАТЕЛЯ ==========

@app.get("/admin/applications", response_class=HTMLResponse)
async def admin_applications(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/employer/login", status_code=303)
    
    current_user = sessions[session_id]
    if current_user.get("role") != "employer":
        return RedirectResponse(url="/", status_code=303)
    
    all_applications = JobService.get_all_applications()
    return templates.TemplateResponse(
        "admin_applications.html",
        {"request": request, "applications": all_applications, "user": current_user}
    )

@app.post("/admin/applications")
async def admin_update_application(
    request: Request,
    app_id: int = Form(...),
    action: str = Form(...)
):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/employer/login", status_code=303)
    
    current_user = sessions[session_id]
    if current_user.get("role") != "employer":
        return RedirectResponse(url="/", status_code=303)
    
    if action == "accept":
        JobService.update_application_status(app_id, "accepted")
        message = f"✅ Заявка #{app_id} принята!"
        
        # Создаем чат
        application = JobService.get_application(app_id)
        if application:
            vacancy = JobService.get_vacancy(application["vacancy_id"])
            JobService.create_chat(
                application_id=app_id,
                student_email=application["student_email"],
                student_name=application["student_name"],
                vacancy_id=application["vacancy_id"],
                vacancy_title=vacancy["title"] if vacancy else f"Вакансия #{application['vacancy_id']}"
            )
    elif action == "reject":
        JobService.update_application_status(app_id, "rejected")
        message = f"❌ Заявка #{app_id} отклонена!"
    else:
        message = "Неизвестное действие"
    
    all_applications = JobService.get_all_applications()
    return templates.TemplateResponse(
        "admin_applications.html",
        {"request": request, "applications": all_applications, "user": current_user, "message": message}
    )

# ========== ЧАТ ==========

@app.get("/chat/{application_id}", response_class=HTMLResponse)
async def chat_page(request: Request, application_id: int):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=303)
    
    current_user = sessions[session_id]
    application = JobService.get_application(application_id)
    if not application:
        return RedirectResponse(url="/", status_code=303)
    
    is_student = (application["student_email"] == current_user.get("email"))
    is_employer = (current_user.get("role") == "employer")
    
    chat = JobService.get_chat_by_application(application_id)
    if not chat:
        vacancy = JobService.get_vacancy(application["vacancy_id"])
        chat = JobService.create_chat(
            application_id=application_id,
            student_email=application["student_email"],
            student_name=application["student_name"],
            vacancy_id=application["vacancy_id"],
            vacancy_title=vacancy["title"] if vacancy else f"Вакансия #{application['vacancy_id']}"
        )
    
    messages = JobService.get_messages_by_application(application_id)
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "application_id": application_id,
        "chat": chat,
        "messages": messages,
        "user": current_user,
        "is_student": is_student,
        "is_employer": is_employer
    })

@app.post("/chat/{application_id}/send")
async def send_message(request: Request, application_id: int, message: str = Form(...)):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=303)
    
    current_user = sessions[session_id]
    application = JobService.get_application(application_id)
    is_student = (application["student_email"] == current_user.get("email"))
    is_employer = (current_user.get("role") == "employer")
    
    sender = "student" if is_student else "employer"
    sender_name = current_user.get("username")
    JobService.add_message(application_id, sender, sender_name, message)
    return RedirectResponse(url=f"/chat/{application_id}", status_code=303)

@app.get("/my-chats", response_class=HTMLResponse)
async def my_chats(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=303)
    
    current_user = sessions[session_id]
    
    if current_user.get("role") == "employer":
        all_chats = JobService.get_all_chats()
        active_chats = []
        for chat in all_chats:
            app = JobService.get_application(chat["application_id"])
            if app and app["status"] == "accepted":
                active_chats.append(chat)
    else:
        active_chats = JobService.get_chats_by_student_email(current_user.get("email"))
    
    return templates.TemplateResponse(
        "my_chats.html",
        {"request": request, "chats": active_chats, "user": current_user}
    )
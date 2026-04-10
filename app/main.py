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

# ========== API ЭНДПОИНТЫ ==========

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
        
        application = JobService.get_application(app_id)
        if application:
            vacancy = JobService.get_vacancy(application.vacancy_id)
            JobService.create_chat(
                application_id=app_id,
                student_email=application.student_email,
                student_name=application.student_name,
                vacancy_id=application.vacancy_id,
                vacancy_title=vacancy.title if vacancy else f"Вакансия #{application.vacancy_id}"
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
    print(f"\n=== ОТЛАДКА ЧАТА ===")
    print(f"Запрошен чат для заявки: {application_id}")
    
    session_id = request.cookies.get("session_id")
    print(f"Session ID: {session_id}")
    print(f"Все сессии: {sessions}")
    
    if not session_id or session_id not in sessions:
        print("ОШИБКА: Сессия не найдена!")
        return RedirectResponse(url="/login", status_code=303)
    
    current_user = sessions[session_id]
    print(f"Текущий пользователь: {current_user}")
    
    # Получаем заявку
    try:
        application = JobService.get_application(application_id)
        print(f"Заявка: {application}")
    except Exception as e:
        print(f"ОШИБКА при получении заявки: {e}")
        return RedirectResponse(url="/", status_code=303)
    
    if not application:
        print("ОШИБКА: Заявка не найдена!")
        return RedirectResponse(url="/", status_code=303)
    
    # Проверяем права доступа
    is_student = (application.student_email == current_user.get("email"))
    is_employer = (current_user.get("role") == "employer")
    print(f"is_student: {is_student}, is_employer: {is_employer}")
    print(f"Email заявки: {application.student_email}")
    print(f"Email пользователя: {current_user.get('email')}")
    
    if not (is_student or is_employer):
        print("ОШИБКА: Нет доступа к чату!")
        return RedirectResponse(url="/", status_code=303)
    
    # Получаем или создаем чат
    try:
        chat = JobService.get_chat_by_application(application_id)
        print(f"Чат из БД: {chat}")
        
        if not chat:
            print("Чат не найден, создаем новый...")
            vacancy = JobService.get_vacancy(application.vacancy_id)
            print(f"Вакансия: {vacancy}")
            chat = JobService.create_chat(
                application_id=application_id,
                student_email=application.student_email,
                student_name=application.student_name,
                vacancy_id=application.vacancy_id,
                vacancy_title=vacancy.title if vacancy else f"Вакансия #{application.vacancy_id}"
            )
            print(f"Созданный чат: {chat}")
        
        messages = JobService.get_messages_by_application(application_id)
        print(f"Сообщений: {len(messages) if messages else 0}")
        
    except Exception as e:
        print(f"ОШИБКА при работе с чатом: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/", status_code=303)
    
    print("=== ОТЛАДКА ЗАВЕРШЕНА ===\n")
    
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "application_id": application_id,
            "chat": chat,
            "messages": messages,
            "user": current_user,
            "is_student": is_student,
            "is_employer": is_employer
        }
    )

@app.post("/chat/{application_id}/send")
async def send_message(
    request: Request,
    application_id: int,
    message: str = Form(...)
):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=303)
    
    current_user = sessions[session_id]
    
    application = JobService.get_application(application_id)
    if not application:
        return RedirectResponse(url="/", status_code=303)
    
    is_student = (application.student_email == current_user.get("email"))
    is_employer = (current_user.get("role") == "employer")
    
    if not (is_student or is_employer):
        return RedirectResponse(url="/", status_code=303)
    
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
            if app and app.status == "accepted":
                active_chats.append(chat)
    else:
        active_chats = JobService.get_chats_by_student_email(current_user.get("email"))
    
    return templates.TemplateResponse(
        "my_chats.html",
        {"request": request, "chats": active_chats, "user": current_user}
    )
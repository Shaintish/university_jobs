from .schemas import VacancyCreate, Vacancy, ApplicationCreate, Application, ApplicationStatus, UserCreate, User
from fastapi import HTTPException

# Имитация БД
vacancies_db = []
applications_db = []
users_db = []
current_session = {}  # {session_id: user_id} - для хранения авторизованных пользователей

# Для чатов
chats_db = []  # Список чатов
messages_db = []


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
    def create_application(data: ApplicationCreate, user_id: int = None) -> Application:
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

    @staticmethod
    def get_application(app_id: int) -> Application:
        application = next((a for a in applications_db if a.id == app_id), None)
        if not application:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return application

    @staticmethod
    def get_applications_by_email(email: str):
        return [a for a in applications_db if a.student_email == email]

    @staticmethod
    def get_all_applications():
        return applications_db

    @staticmethod
    def update_application_status(app_id: int, new_status: str) -> Application:
        for app in applications_db:
            if app.id == app_id:
                app.status = new_status
                return app
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    # Методы для чата
    @staticmethod
    def create_chat(application_id: int, student_email: str, student_name: str, vacancy_id: int, vacancy_title: str):
        """Создает чат для принятой заявки"""
        for chat in chats_db:
            if chat["application_id"] == application_id:
                return chat

        new_chat = {
            "application_id": application_id,
            "student_email": student_email,
            "student_name": student_name,
            "vacancy_id": vacancy_id,
            "vacancy_title": vacancy_title,
            "messages": []
        }
        chats_db.append(new_chat)
        return new_chat

    @staticmethod
    def get_chat_by_application(application_id: int):
        for chat in chats_db:
            if chat["application_id"] == application_id:
                return chat
        return None

    @staticmethod
    def get_chats_by_student_email(email: str):
        return [chat for chat in chats_db if chat["student_email"] == email]

    @staticmethod
    def get_all_chats():
        return chats_db

    @staticmethod
    def add_message(application_id: int, sender: str, sender_name: str, text: str):
        from datetime import datetime
        new_id = len(messages_db) + 1
        timestamp = datetime.now().strftime("%H:%M:%S %d.%m.%Y")

        message = {
            "id": new_id,
            "application_id": application_id,
            "sender": sender,
            "sender_name": sender_name,
            "text": text,
            "timestamp": timestamp
        }
        messages_db.append(message)

        for chat in chats_db:
            if chat["application_id"] == application_id:
                if "messages" not in chat:
                    chat["messages"] = []
                chat["messages"].append(message)
                break

        return message

    @staticmethod
    def get_messages_by_application(application_id: int):
        return [msg for msg in messages_db if msg["application_id"] == application_id]


class UserService:
    @staticmethod
    def register(data: UserCreate) -> User:
        # Проверка: существует ли пользователь
        for user in users_db:
            if user.username == data.username:
                raise HTTPException(status_code=400, detail="Пользователь уже существует")
            if user.email == data.email:
                raise HTTPException(status_code=400, detail="Email уже используется")

        new_id = len(users_db) + 1
        user = User(id=new_id, username=data.username, email=data.email)
        users_db.append(user)

        # Сохраняем пароль отдельно (в реальном проекте хешируем!)
        user_password = {"id": new_id, "username": data.username, "password": data.password}
        if not hasattr(UserService, 'passwords'):
            UserService.passwords = []
        UserService.passwords.append(user_password)

        return user

    @staticmethod
    def login(username: str, password: str):
        for user in users_db:
            if user.username == username:
                for pwd in UserService.passwords:
                    if pwd["username"] == username and pwd["password"] == password:
                        return user
                raise HTTPException(status_code=401, detail="Неверный пароль")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    @staticmethod
    def get_user_by_username(username: str):
        for user in users_db:
            if user.username == username:
                return user
        return None
    @staticmethod
    def get_all_applications():
        return applications_db

@staticmethod
def update_application_status(app_id: int, new_status: str) -> Application:
    for app in applications_db:
        if app.id == app_id:
            app.status = new_status
            return app
    raise HTTPException(status_code=404, detail="Заявка не найдена")

@staticmethod
def create_chat(application_id: int, student_email: str, student_name: str, vacancy_id: int, vacancy_title: str):
    for chat in chats_db:
        if chat["application_id"] == application_id:
            return chat
    new_chat = {
        "application_id": application_id,
        "student_email": student_email,
        "student_name": student_name,
        "vacancy_id": vacancy_id,
        "vacancy_title": vacancy_title,
        "messages": []
    }
    chats_db.append(new_chat)
    return new_chat

@staticmethod
def get_chat_by_application(application_id: int):
    for chat in chats_db:
        if chat["application_id"] == application_id:
            return chat
    return None

@staticmethod
def get_chats_by_student_email(email: str):
    return [chat for chat in chats_db if chat["student_email"] == email]

@staticmethod
def get_all_chats():
    return chats_db

@staticmethod
def add_message(application_id: int, sender: str, sender_name: str, text: str):
    from datetime import datetime
    new_id = len(messages_db) + 1
    timestamp = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    message = {
        "id": new_id,
        "application_id": application_id,
        "sender": sender,
        "sender_name": sender_name,
        "text": text,
        "timestamp": timestamp
    }
    messages_db.append(message)
    for chat in chats_db:
        if chat["application_id"] == application_id:
            if "messages" not in chat:
                chat["messages"] = []
            chat["messages"].append(message)
            break
    return message

@staticmethod
def get_messages_by_application(application_id: int):
    return [msg for msg in messages_db if msg["application_id"] == application_id]
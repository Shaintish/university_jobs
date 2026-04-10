import sqlite3

DB_NAME = "careerhub.db"

def get_db():
    """Подключение к базе данных"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создание всех таблиц"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица вакансий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            department TEXT NOT NULL,
            job_type TEXT NOT NULL,
            salary INTEGER,
            employer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица чатов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER UNIQUE NOT NULL,
            student_email TEXT NOT NULL,
            student_name TEXT NOT NULL,
            vacancy_id INTEGER NOT NULL,
            vacancy_title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            message_text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавляем тестового работодателя
    cursor.execute("SELECT * FROM users WHERE username = 'employer'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', ('employer', 'employer@company.com', 'admin123', 'employer'))
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована!")

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========
def save_user(username, email, password, role='student'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    ''', (username, email, password, role))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ВАКАНСИЯМИ ==========
def save_vacancy(title, description, department, job_type, salary, employer_id=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vacancies (title, description, department, job_type, salary, employer_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, department, job_type, salary, employer_id))
    conn.commit()
    vacancy_id = cursor.lastrowid
    conn.close()
    return vacancy_id

def get_all_vacancies(search=None):
    conn = get_db()
    cursor = conn.cursor()
    if search:
        cursor.execute('''
            SELECT * FROM vacancies 
            WHERE title LIKE ? OR department LIKE ?
            ORDER BY id DESC
        ''', (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT * FROM vacancies ORDER BY id DESC")
    vacancies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return vacancies

def get_vacancy(vacancy_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vacancies WHERE id = ?", (vacancy_id,))
    vacancy = cursor.fetchone()
    conn.close()
    return dict(vacancy) if vacancy else None

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ЗАЯВКАМИ ==========
def save_application(vacancy_id, student_name, student_email, status='pending'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (vacancy_id, student_name, student_email, status)
        VALUES (?, ?, ?, ?)
    ''', (vacancy_id, student_name, student_email, status))
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return app_id

def get_applications_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM applications 
        WHERE student_email = ? 
        ORDER BY id DESC
    ''', (email,))
    apps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return apps

def get_all_applications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY id DESC")
    apps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return apps

def update_application_status(app_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE applications SET status = ? WHERE id = ?
    ''', (status, app_id))
    conn.commit()
    conn.close()

def get_application(app_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    app = cursor.fetchone()
    conn.close()
    return dict(app) if app else None

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ЧАТАМИ ==========
def save_chat(application_id, student_email, student_name, vacancy_id, vacancy_title):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO chats (application_id, student_email, student_name, vacancy_id, vacancy_title)
        VALUES (?, ?, ?, ?, ?)
    ''', (application_id, student_email, student_name, vacancy_id, vacancy_title))
    conn.commit()
    conn.close()

def get_chat_by_application(application_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE application_id = ?", (application_id,))
    chat = cursor.fetchone()
    conn.close()
    return dict(chat) if chat else None

def get_chats_by_student_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE student_email = ?", (email,))
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return chats

def get_all_chats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats")
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return chats

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С СООБЩЕНИЯМИ ==========
def save_message(application_id, sender, sender_name, message_text):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (application_id, sender, sender_name, message_text)
        VALUES (?, ?, ?, ?)
    ''', (application_id, sender, sender_name, message_text))
    conn.commit()
    conn.close()

def get_messages_by_application(application_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM messages 
        WHERE application_id = ? 
        ORDER BY timestamp ASC
    ''', (application_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

# Инициализация БД при импорте модуля
init_db()
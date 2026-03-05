# University Career Hub API

API для центра карьеры университета.

##1.зависимости установить
```bash
pip install -r requirements.txt

##2.запустить сам сервис**
```bash
uvicorn app.main:app --reload

##3.запуск теста
```bash
python -m pytest tests/test_main.py
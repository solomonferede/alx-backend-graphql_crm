# CRM Celery Report Generator

## Prerequisites

- Python 3.10+
- Redis

## Install Redis

```bash
sudo apt update
sudo apt install redis-server
redis-server
Install Dependencies
bash
Copy code
pip install -r requirements.txt
Run Migrations
bash
Copy code
python manage.py migrate
Start Django Server
bash
Copy code
python manage.py runserver
Start Celery Worker
bash
Copy code
celery -A crm worker -l info
Start Celery Beat
bash
Copy code
celery -A crm beat -l info
```

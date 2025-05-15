# 📬 Email Processing Backend API

This is a Django REST Framework-based backend service that processes email-related actions. It receives requests from the frontend to either retrieve email content, view specific emails, or update and send responses. Authentication is implemented for secure access.

Deployment is containerized using Docker and served behind Nginx as a reverse proxy.

---

## 🚀 Features

- ✅ User authentication and verification
- 📥 Fetch all email contents
- 📄 Retrieve a specific email by ID
- ✏️ Update and send reply to an email via Microsoft Graph API
- 🔐 Secure endpoint for token-authenticated access
- 🐳 Dockerized deployment
- 🌐 Served through Nginx

---

## 📁 API Endpoints

| Method | Endpoint                                      | Description                              |
|--------|-----------------------------------------------|------------------------------------------|
| POST   | /api/check_user/                              | Authenticate and verify the user         |
| GET    | /api/secure/                                  | Token-protected secure test endpoint     |
| GET    | /api/email-contents/                          | Retrieve all email entries               |
| GET    | /api/email-contents/<int:pk>/                 | Retrieve specific email by ID            |
| POST   | /api/email-contents/update/<int:pk>/          | Update and send reply to an email        |

---

## 🐳 Dockerized Deployment

The backend app is containerized and served behind Nginx.

### 📦 Docker Folder Structure

project-root/
├── backend/
│ ├── manage.py
│ ├── myapp/
│ └── ...
├── nginx/
│ └── default.conf
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

sql
Copy
Edit

### 🔧 Dockerfile (Django App)

```Dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
🌐 Nginx Configuration (nginx/default.conf)
nginx
Copy
Edit
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
🧱 docker-compose.yml
yaml
Copy
Edit
version: '3.8'

services:
  web:
    build: .
    container_name: django_app
    volumes:
      - .:/app
    expose:
      - 8000
    depends_on:
      - nginx

  nginx:
    image: nginx:latest
    container_name: nginx_server
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
▶️ Running the Project with Docker
Build and start containers:

bash
Copy
Edit
docker-compose up --build
Access the API at:

http://localhost/api/

✅ Requirements (non-Docker local setup)
Python 3.10+

Django 4+

Django REST Framework

sentence-transformers

MSAL (Microsoft Authentication Library)

Pandas, openpyxl, boto3

🔐 Authentication
Uses token-based authentication.

Authorization headers must be passed with each request to access secure endpoints.

Example:

http
Copy
Edit
Authorization: Bearer <your-token>
📦 Future Enhancements
Swagger/OpenAPI documentation

Unit tests and CI

JWT Authentication

Celery for asynchronous processing


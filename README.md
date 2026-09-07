# News Application Capstone

## Project Overview

The News Application is a Django capstone project that provides a role-based news publishing system. The application allows users to view approved articles, while journalists and editors have additional permissions for managing article content through a Django REST Framework API.

The project demonstrates:

- Django web application structure
- MariaDB database integration
- Custom user roles
- Django REST Framework API endpoints
- Token-based API authentication
- Role-based permissions
- Automated testing
- CRUD functionality for article management
- Subscription-based article filtering

## Folder Structure

```text
Capstone News project/
|-- news/
|   |-- migrations/
|   |-- admin.py
|   |-- apps.py
|   |-- models.py
|   |-- permissions.py
|   |-- serializers.py
|   |-- tests.py
|   |-- urls.py
|   |-- views.py
|
|-- news_project/
|   |-- settings.py
|   |-- urls.py
|   |-- wsgi.py
|   |-- asgi.py
|
|-- Planning/
|   |-- research_answers.docx
|   |-- CRUD diagrams
|
|-- Screenshots/
|   |-- API testing screenshots
|   |-- MariaDB screenshots
|   |-- Test result screenshots
|
|-- manage.py
|-- Requirements.txt
|-- README.md
```

## Technologies Used

- Python 3.11
- Django 5.2
- Django REST Framework
- MariaDB
- mysqlclient
- Token Authentication
- Git and GitHub

## Requirements

Create a `Requirements.txt` file in the project root with:

```text
Django>=5.2,<6.0
djangorestframework>=3.15.0
mysqlclient>=2.2.0
```

## Setup Instructions

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r Requirements.txt
```

### 3. Configure MariaDB

Ensure MariaDB is running and create a database named:

```sql
news_db
```

The Django `settings.py` database configuration should point to the MariaDB database.

### 4. Apply migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser

```powershell
python manage.py createsuperuser
```

### 6. Run the development server

```powershell
python manage.py runserver
```

Open the application in a browser at:

```text
http://127.0.0.1:8000/
```

## User Roles

The application uses custom user roles to control access.

| Role | Description |
|---|---|
| Reader | Can view approved articles and subscribed articles. Cannot create, update or delete articles. |
| Journalist | Can create articles, update articles and delete articles. |
| Editor | Can update and delete articles. Editor users are not allowed to create articles in the tested role design. |
| Root/Admin | Administrative account used for Django admin tasks. |

## API Endpoints

| Method | Endpoint | Purpose | Permission |
|---|---|---|---|
| GET | `/api/articles/` | List approved articles | Authenticated user |
| POST | `/api/articles/` | Create a new article | Journalist |
| GET | `/api/articles/<id>/` | View one article | Authenticated user |
| PUT/PATCH | `/api/articles/<id>/` | Update an article | Journalist or Editor |
| DELETE | `/api/articles/<id>/` | Delete an article | Journalist or Editor |
| GET | `/api/articles/subscribed/` | View subscribed articles | Authenticated user |

## Token Authentication

API requests are authenticated using DRF Token Authentication.

Example header:

```text
Authorization: Token <token_value>
```

For screenshots, the token should be partially hidden or blurred to avoid exposing the full value.

## API Testing Evidence

The following behaviours were tested using API requests:

- Reader can read articles.
- Reader cannot create articles.
- Reader cannot update articles.
- Journalist can create articles.
- Journalist can update articles.
- Journalist can delete articles.
- Editor can update articles.
- Editor can delete articles.
- Editor cannot create articles.
- Subscribed articles endpoint returns valid JSON.
- Unauthenticated requests are rejected where authentication is required.

## MariaDB Evidence

The project includes screenshots showing:

- MariaDB connection
- `SHOW DATABASES;`
- `USE news_db;`
- `SHOW TABLES;`
- Django tables and application tables created inside MariaDB

## Running Tests

Run automated tests with:

```powershell
python manage.py test
```

The screenshot evidence shows that the Django system check completed successfully and the automated tests were executed.

## CRUD Summary

| CRUD Operation | API Method | Endpoint | Role |
|---|---|---|---|
| Create | POST | `/api/articles/` | Journalist |
| Read | GET | `/api/articles/` and `/api/articles/<id>/` | Authenticated user |
| Update | PUT/PATCH | `/api/articles/<id>/` | Journalist or Editor |
| Delete | DELETE | `/api/articles/<id>/` | Journalist or Editor |

## Submission Checklist

- [x] Source code included
- [x] `Requirements.txt` included
- [x] MariaDB configured
- [x] API endpoints tested
- [x] Role-based access screenshots captured
- [x] Automated tests screenshot captured
- [x] README created
- [x] Research answers document created
- [x] CRUD diagrams created

## Notes

This project demonstrates the use of Django REST Framework to expose secure API endpoints for a news application. Role-based permissions protect article management operations so that only authorised users can create, update or delete article records.

# LocaParticuliers - Django Backend Project

A Django-based rental property management system with features for properties, reservations, messaging, reviews, and payments.

## Project Structure

```
backend/
├── base/                 # Base app (home page, general features)
├── properties/           # Property listings and management
├── reservations/         # Booking and reservation system
├── messaging/            # User-to-user messaging
├── reviews/              # Property reviews system
├── paiement/             # Payment processing
├── users/                # Custom user model and authentication
└── static/               # CSS, JavaScript, images
```

## Setup & Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Configuration

The project is configured to use **MySQL** database:
- Database: `db_location`
- User: `root`
- Host: `localhost`
- Port: `3306`

Update credentials in `backend/backend/settings.py` if needed.

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
python manage.py runserver
```

Server will run at: **http://127.0.0.1:8000/**

Admin panel: **http://127.0.0.1:8000/admin/**

## Key Features

- **User Management**: Custom user model with authentication
- **Properties**: List, manage, and search rental properties
- **Reservations**: Booking system with confirmation workflow
- **Messaging**: Direct messaging between users
- **Reviews**: Property and user rating system
- **Payments**: Payment processing integration
- **Admin Panel**: Django admin for content management

## Environment Variables

Create a `.env` file in the project root:
```
ADMIN_SIGNUP_SECRET=your-secret-key
DEBUG=True
```

## Common Commands

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Collect static files (production)
python manage.py collectstatic

# Run tests
python manage.py test

# Create new app
python manage.py startapp app_name
```

## Configuration

Main settings file: `backend/backend/settings.py`

- **Language**: French (fr-fr)
- **Timezone**: Europe/Paris
- **Authentication**: Custom user model (`users.CustomUser`)
- **Templates**: Bootstrap 5 with Crispy Forms

## Dependencies

See `requirements.txt` for full list. Main packages:
- Django 6.0.3+
- Django Crispy Forms
- MySQLdb (MySQL connector)
- Other utilities

## Support

For issues or questions, refer to the Django documentation:
https://docs.djangoproject.com/en/6.0/

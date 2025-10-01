# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Django Management
```bash
# Run development server
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test users
python manage.py test organizations_management

# Run specific test class
python manage.py test users.tests.tests.UserObjectsTestCase

# Load fixtures (test data)
python manage.py loaddata users
python manage.py loaddata organizations
```

### API Documentation
```bash
# Generate/update API schema
python manage.py spectacular --file schema.yml

# Access API documentation:
# Swagger UI: http://localhost:8000/api/schema/swagger-ui/
# ReDoc: http://localhost:8000/api/schema/redoc/
# Schema download: http://localhost:8000/api/schema/
```

## Project Architecture

### Django Apps Structure
- **users**: Custom User model with UUID primary keys, profile image handling via S3
- **organizations_management**: Organizations and Projects management with hierarchical permissions
- **files**: File upload/download functionality with S3 integration
- **root_project**: Main Django project configuration

### API Design
- **Versioned APIs**: All endpoints under `/api/v1/` namespace
- **Authentication**: JWT-based with access/refresh tokens
- **ViewSets**: DRF ViewSet architecture with DefaultRouter
- **Permissions**: Custom permission classes for organization/project access

### Key Models
- **User**: Extended AbstractUser with UUID primary key and profile image URL
- **Organization**: UUID-based with owner/admins/members relationships
- **Project**: Belongs to Organization, creates S3 buckets automatically
- **Relationships**: Organizations → Projects hierarchy with permission inheritance

### URL Structure
```
/api/token/                          # JWT token obtain/refresh
/api/v1/users/                       # User management endpoints
/api/v1/organizations/               # Organization CRUD
/api/v1/organizations/{id}/projects/ # Project management per organization
```

### S3 Integration
- **Local Development**: Uses localstack/minio via S3_LOCAL_* environment variables
- **Production**: Standard AWS S3 configuration
- **Helpers**: `organizations_management.helpers` provides presigned URL generation
- **Auto-bucket**: Organizations automatically create S3 buckets on creation

### Authentication Flow
1. POST `/api/token/` with username/password → receive access/refresh tokens
2. Include `Authorization: Bearer <access_token>` in API requests
3. Refresh tokens via POST `/api/token/refresh/`

### Testing Patterns
- **Test Organization**: Tests separated by app in `app/tests/` directories
- **Fixtures**: Pre-loaded test data in `app/fixtures/` (149 users, organizations)
- **TestCase Classes**: Standard Django TestCase with fixture loading
- **Custom Assertions**: UUID validation, relationship testing

### Development Environment
- **Python**: 3.11.9 required
- **Database**: SQLite for development (db.sqlite3)
- **Dependencies**: See requirements.txt for DRF, JWT, S3, API documentation tools
- **Environment Variables**: Managed via python-decouple (.env file)
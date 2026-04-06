# Finance Dashboard API

A REST API backend for a finance dashboard system built with FastAPI, MySQL, and SQLAlchemy.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python) |
| Database | MySQL |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose) |
| Password Hashing | bcrypt (passlib) |
| Validation | Pydantic v2 |

---

## Project Structure

finance-dashboard/
├── app/
│   ├── main.py            # App entry point, router registration
│   ├── database.py        # DB connection and session
│   ├── models.py          # SQLAlchemy table definitions
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py        # Register, login
│   │   ├── users.py       # User management
│   │   ├── records.py     # Financial records CRUD
│   │   └── dashboard.py   # Summary and analytics
│   └── middleware/
│       └── auth.py        # JWT verification and RBAC
├── .env                   # Environment variables (not committed)
├── requirements.txt
└── README.md

---

## Local Setup

### 1. Clone and create virtual environment
```bash
git clone <your-repo-url>
cd finance-dashboard
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create MySQL database
```sql
CREATE DATABASE finance_db;
```

### 4. Create `.env` file
```env
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/finance_db
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

---

## Generate requirements.txt
```bash
pip freeze > requirements.txt
```

---

## Roles and Permissions

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| Register / Login | ✅ | ✅ | ✅ |
| View own records | ✅ | ✅ | ✅ |
| View all records | ❌ | ❌ | ✅ |
| Create records | ❌ | ✅ | ✅ |
| Update records | ❌ | own only | ✅ |
| Delete records | ❌ | ❌ | ✅ |
| View dashboard summary | ✅ | ✅ | ✅ |
| View trends | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## API Endpoints

### Auth
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Create new account |
| POST | `/auth/login` | Public | Login and get token |

### Users
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/users/me` | All | Get own profile |
| GET | `/users/` | Admin | List all users |
| PATCH | `/users/{id}/role` | Admin | Change user role |
| PATCH | `/users/{id}/status` | Admin | Activate/deactivate user |
| DELETE | `/users/{id}` | Admin | Delete user |

### Financial Records
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/records/` | Admin, Analyst | Create a record |
| GET | `/records/` | All | List records (with filters) |
| GET | `/records/{id}` | All | Get single record |
| PATCH | `/records/{id}` | Admin, Analyst | Update a record |
| DELETE | `/records/{id}` | Admin | Soft delete a record |

#### Record filters (query params)

GET /records/?type=income
GET /records/?category=salary
GET /records/?from_date=2024-01-01&to_date=2024-12-31
GET /records/?page=1&limit=10

### Dashboard
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/dashboard/summary` | All | Total income, expense, balance |
| GET | `/dashboard/categories` | All | Totals grouped by category |
| GET | `/dashboard/trends` | Analyst, Admin | Monthly breakdown by year |
| GET | `/dashboard/recent` | All | Latest N records |

---

## Example Requests

### Register
```json
POST /auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secret123"
}
```

### Login
```json
POST /auth/login
{
  "email": "john@example.com",
  "password": "secret123"
}
```

### Create a record
```json
POST /records/
Authorization: Bearer <token>
{
  "amount": 5000,
  "type": "income",
  "category": "salary",
  "date": "2024-01-15",
  "notes": "January salary"
}
```

### Dashboard summary response
```json
GET /dashboard/summary
{
  "income": 15000.00,
  "expense": 4200.00,
  "balance": 10800.00
}
```

---

## Assumptions and Design Decisions

1. **Soft deletes** — financial records are never truly deleted. A `deleted_at` timestamp is set instead so history is always preserved.

2. **Role visibility** — viewers and analysts only see their own records. Admins see all records across all users.

3. **JWT Auth** — tokens are passed as Bearer tokens in the Authorization header. Tokens expire after 60 minutes by default.

4. **Amount precision** — stored as `NUMERIC(12, 2)` in MySQL to avoid floating point issues with money.

5. **Default role** — newly registered users get the `viewer` role. An admin must manually promote them.

6. **Self-protection** — admins cannot deactivate or delete their own account to prevent lockout.

7. **Pagination** — record listing defaults to 10 per page with a max of 100.

---

## What I Would Add With More Time

- Refresh tokens
- Search records by keyword
- Export records to CSV
- Unit and integration tests
- Rate limiting
- Admin seed script

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import auth, records, dashboard, users
import traceback

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Dashboard API")

app.include_router(auth.router)
app.include_router(records.router)
app.include_router(dashboard.router)
app.include_router(users.router)

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/")
def root():
    return {"message": "Finance Dashboard API is running"}
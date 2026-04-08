from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine

from app.models.project import Project
from app.models.asset import Asset
from app.models.check_template import CheckTemplate
from app.models.check_record import CheckRecord

from app.api.project import router as project_router
from app.api.asset import router as asset_router
from app.api.template import router as template_router
from app.api.record import router as record_router

from app.api.stats import router as stats_router
from app.api.ai import router as ai_router

from app.models.user import User
from app.api.user import router as user_router

app = FastAPI(title="等级保护测评辅助系统")
app.include_router(ai_router)
app.include_router(user_router)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router)
app.include_router(asset_router)
app.include_router(template_router)
app.include_router(record_router)
app.include_router(stats_router)

@app.get("/")
def root():
    return {"message": "Backend is running"}
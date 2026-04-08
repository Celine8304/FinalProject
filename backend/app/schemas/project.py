from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    project_code: str
    project_name: str
    system_name: Optional[str] = None
    organization_name: Optional[str] = None
    level: Optional[str] = None
    standard_system: Optional[str] = None
    is_archived: Optional[bool] = False
    user_id: int | None = None


class ProjectUpdate(BaseModel):
    project_code: Optional[str] = None
    project_name: Optional[str] = None
    system_name: Optional[str] = None
    organization_name: Optional[str] = None
    level: Optional[str] = None
    standard_system: Optional[str] = None
    is_archived: Optional[bool] = None
    user_id: int | None = None


class ProjectResponse(BaseModel):
    id: int
    project_code: str
    project_name: str
    system_name: Optional[str] = None
    organization_name: Optional[str] = None
    level: Optional[str] = None
    standard_system: Optional[str] = None
    created_at: datetime
    is_archived: bool
    user_id: int | None = None

    class Config:
        from_attributes = True
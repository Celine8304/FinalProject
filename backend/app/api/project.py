from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    existing_project = db.query(Project).filter(Project.project_code == project.project_code).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="项目编号已存在")

    new_project = Project(
        project_code=project.project_code,
        project_name=project.project_name,
        system_name=project.system_name,
        organization_name=project.organization_name,
        level=project.level,
        standard_system=project.standard_system,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.id.desc()).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if payload.project_code is not None and payload.project_code != project.project_code:
        existing_project = db.query(Project).filter(Project.project_code == payload.project_code).first()
        if existing_project:
            raise HTTPException(status_code=400, detail="项目编号已存在")
        project.project_code = payload.project_code

    if payload.project_name is not None:
        project.project_name = payload.project_name

    if payload.system_name is not None:
        project.system_name = payload.system_name

    if payload.organization_name is not None:
        project.organization_name = payload.organization_name

    if payload.level is not None:
        project.level = payload.level

    if payload.standard_system is not None:
        project.standard_system = payload.standard_system

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    db.delete(project)
    db.commit()

    return {"message": "项目删除成功"}

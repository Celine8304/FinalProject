from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from datetime import datetime
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("user_id", "project_code", name="uq_projects_user_project_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(100), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    system_name = Column(String(200), nullable=True, comment="系统名称")
    organization_name = Column(String(200), nullable=True, comment="被测单位")
    level = Column(String(50), nullable=True, comment="等级")
    standard_system = Column(String(100), nullable=True, comment="标准体系")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    is_archived = Column(Boolean, default=False, nullable=False, comment="是否归档")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="所属用户ID")
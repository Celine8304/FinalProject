from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(100), nullable=False, unique=True, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    system_name = Column(String(200), nullable=True, comment="系统名称")
    organization_name = Column(String(200), nullable=True, comment="被测单位")
    level = Column(String(50), nullable=True, comment="等级")
    standard_system = Column(String(100), nullable=True, comment="标准体系")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
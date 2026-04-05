from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="所属项目ID")
    asset_type = Column(String(50), nullable=False, comment="资产类型：server_storage / database")
    asset_name = Column(String(200), nullable=False, comment="资产名称")
    ip_address = Column(String(100), nullable=True, comment="IP地址")
    os_or_db_type = Column(String(100), nullable=True, comment="操作系统或数据库类型")
    remark = Column(String(500), nullable=True, comment="备注")

    project = relationship("Project", backref="assets")
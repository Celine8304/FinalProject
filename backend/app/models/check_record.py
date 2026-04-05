from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class CheckRecord(Base):
    __tablename__ = "check_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="项目ID")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="资产ID")
    template_id = Column(Integer, ForeignKey("check_templates.id"), nullable=False, comment="模板ID")

    result_record = Column(Text, nullable=True, comment="结果记录")
    compliance_status = Column(String(50), nullable=True, comment="符合情况：compliant / partial / non_compliant")
    record_remark = Column(Text, nullable=True, comment="核查备注")
    ai_suggestion = Column(Text, nullable=True, comment="AI整改建议")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    project = relationship("Project", backref="check_records")
    asset = relationship("Asset", backref="check_records")
    template = relationship("CheckTemplate", backref="check_records")
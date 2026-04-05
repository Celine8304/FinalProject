from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class CheckTemplate(Base):
    __tablename__ = "check_templates"

    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(50), nullable=False, comment="资产类型")
    guide_name = Column(String(200), nullable=False, comment="作业指导书名称")
    sheet_name = Column(String(200), nullable=True, comment="Excel sheet名称")
    seq_no = Column(String(50), nullable=True, comment="序号")
    control_point = Column(String(500), nullable=True, comment="控制点")
    control_item = Column(String(500), nullable=True, comment="控制项")
    importance_level = Column(String(50), nullable=True, comment="重要程度")
    check_content = Column(Text, nullable=True, comment="检查内容")
    judgment_standard = Column(Text, nullable=True, comment="判断标准")
    remark = Column(Text, nullable=True, comment="备注")
    weight = Column(String(50), nullable=True, comment="权重")

    check_method = Column(Text, nullable=True, comment="检查方法")
    recommended_value = Column(Text, nullable=True, comment="推荐值")
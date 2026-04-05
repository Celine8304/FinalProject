from pydantic import BaseModel
from typing import Optional


class TemplateResponse(BaseModel):
    id: int
    asset_type: str
    guide_name: str
    sheet_name: Optional[str] = None
    seq_no: Optional[str] = None
    control_point: Optional[str] = None
    control_item: Optional[str] = None
    importance_level: Optional[str] = None
    check_content: Optional[str] = None
    judgment_standard: Optional[str] = None
    remark: Optional[str] = None
    check_method: Optional[str] = None
    recommended_value: Optional[str] = None
    weight: Optional[str] = None

    class Config:
        from_attributes = True
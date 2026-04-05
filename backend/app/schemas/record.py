from pydantic import BaseModel
from typing import Optional


class CheckRecordUpdate(BaseModel):
    result_record: Optional[str] = None
    compliance_status: Optional[str] = None
    record_remark: Optional[str] = None


class CheckRecordResponse(BaseModel):
    id: int
    project_id: int
    asset_id: int
    template_id: int
    result_record: Optional[str] = None
    compliance_status: Optional[str] = None
    record_remark: Optional[str] = None
    ai_suggestion: Optional[str] = None

    seq_no: Optional[str] = None
    control_point: Optional[str] = None
    control_item: Optional[str] = None
    importance_level: Optional[str] = None
    check_content: Optional[str] = None
    judgment_standard: Optional[str] = None
    template_remark: Optional[str] = None

    class Config:
        from_attributes = True
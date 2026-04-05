from pydantic import BaseModel
from typing import Optional


class AssetCreate(BaseModel):
    project_id: int
    asset_type: str
    asset_name: str
    ip_address: Optional[str] = None
    os_or_db_type: Optional[str] = None
    remark: Optional[str] = None


class AssetUpdate(BaseModel):
    asset_type: Optional[str] = None
    asset_name: Optional[str] = None
    ip_address: Optional[str] = None
    os_or_db_type: Optional[str] = None
    remark: Optional[str] = None


class AssetResponse(BaseModel):
    id: int
    project_id: int
    asset_type: str
    asset_name: str
    ip_address: Optional[str] = None
    os_or_db_type: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True
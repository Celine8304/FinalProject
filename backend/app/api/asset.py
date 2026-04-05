from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import Asset
from app.models.project import Project
from app.models.check_record import CheckRecord
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.services.record_generate_service import generate_records_for_asset

router = APIRouter(prefix="/assets", tags=["资产管理"])


@router.post("/")
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == asset.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="所属项目不存在")

    if asset.asset_type not in ["server_storage", "database"]:
        raise HTTPException(status_code=400, detail="资产类型只能是 server_storage 或 database")

    new_asset = Asset(
        project_id=asset.project_id,
        asset_type=asset.asset_type,
        asset_name=asset.asset_name,
        ip_address=asset.ip_address,
        os_or_db_type=asset.os_or_db_type,
        remark=asset.remark,
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    try:
        generated_count = generate_records_for_asset(new_asset, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "资产创建成功，并已自动生成核查记录",
        "asset": {
            "id": new_asset.id,
            "project_id": new_asset.project_id,
            "asset_type": new_asset.asset_type,
            "asset_name": new_asset.asset_name,
            "ip_address": new_asset.ip_address,
            "os_or_db_type": new_asset.os_or_db_type,
            "remark": new_asset.remark,
        },
        "generated_record_count": generated_count
    }


@router.get("/project/{project_id}", response_model=list[AssetResponse])
def list_assets_by_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    assets = db.query(Asset).filter(Asset.project_id == project_id).order_by(Asset.id.desc()).all()
    return assets

@router.get("/project/{project_id}/progress")
def list_asset_progress_by_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    assets = (
        db.query(Asset)
        .filter(Asset.project_id == project_id)
        .order_by(Asset.id.desc())
        .all()
    )

    result = []
    for asset in assets:
        total_count = (
            db.query(CheckRecord)
            .filter(CheckRecord.asset_id == asset.id)
            .count()
        )

        completed_count = (
            db.query(CheckRecord)
            .filter(
                CheckRecord.asset_id == asset.id,
                CheckRecord.compliance_status.isnot(None),
                CheckRecord.compliance_status != ""
            )
            .count()
        )

        result.append({
            "asset_id": asset.id,
            "total_count": total_count,
            "completed_count": completed_count
        })

    return result

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    old_asset_type = asset.asset_type
    old_guide_name = asset.os_or_db_type

    if payload.asset_type is not None:
        if payload.asset_type not in ["server_storage", "database"]:
            raise HTTPException(status_code=400, detail="资产类型只能是 server_storage 或 database")
        asset.asset_type = payload.asset_type

    if payload.asset_name is not None:
        asset.asset_name = payload.asset_name

    if payload.ip_address is not None:
        asset.ip_address = payload.ip_address

    if payload.os_or_db_type is not None:
        asset.os_or_db_type = payload.os_or_db_type

    if payload.remark is not None:
        asset.remark = payload.remark

    db.commit()
    db.refresh(asset)

    if asset.asset_type != old_asset_type or asset.os_or_db_type != old_guide_name:
        try:
            generate_records_for_asset(asset, db)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return asset


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    db.query(CheckRecord).filter(CheckRecord.asset_id == asset.id).delete()
    db.delete(asset)
    db.commit()

    return {"message": "资产删除成功"}
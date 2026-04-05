from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.asset import Asset
from app.models.check_record import CheckRecord

router = APIRouter(prefix="/stats", tags=["结果统计"])


@router.get("/project/{project_id}")
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    assets = (
        db.query(Asset)
        .filter(Asset.project_id == project_id)
        .order_by(Asset.id.desc())
        .all()
    )

    asset_stats = []

    asset_total = len(assets)
    record_total = 0
    completed_total = 0
    compliant_total = 0
    partial_total = 0
    non_compliant_total = 0

    for asset in assets:
        records = db.query(CheckRecord).filter(CheckRecord.asset_id == asset.id).all()

        total_count = len(records)
        completed_count = sum(1 for r in records if r.compliance_status not in [None, ""])
        compliant_count = sum(1 for r in records if r.compliance_status == "compliant")
        partial_count = sum(1 for r in records if r.compliance_status == "partial")
        non_compliant_count = sum(1 for r in records if r.compliance_status == "non_compliant")

        record_total += total_count
        completed_total += completed_count
        compliant_total += compliant_count
        partial_total += partial_count
        non_compliant_total += non_compliant_count

        asset_stats.append({
            "asset_id": asset.id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "os_or_db_type": asset.os_or_db_type,
            "record_total": total_count,
            "completed_total": completed_count,
            "compliant_total": compliant_count,
            "partial_total": partial_count,
            "non_compliant_total": non_compliant_count
        })

    return {
        "summary": {
            "asset_total": asset_total,
            "record_total": record_total,
            "completed_total": completed_total,
            "compliant_total": compliant_total,
            "partial_total": partial_total,
            "non_compliant_total": non_compliant_total
        },
        "asset_stats": asset_stats
    }
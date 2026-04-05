from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.check_template import CheckTemplate
from app.models.check_record import CheckRecord


def generate_records_for_asset(asset: Asset, db: Session) -> int:
    """
    根据资产的 asset_type + os_or_db_type（作业指导书类型）
    自动匹配模板，并生成该资产的核查记录
    返回生成的记录数
    """

    guide_name = asset.os_or_db_type

    if not guide_name:
        raise ValueError("资产未填写作业指导书类型，无法绑定模板")

    templates = (
        db.query(CheckTemplate)
        .filter(
            CheckTemplate.asset_type == asset.asset_type,
            CheckTemplate.guide_name == guide_name
        )
        .order_by(CheckTemplate.id.asc())
        .all()
    )

    if not templates:
        raise ValueError(f"未找到匹配模板：asset_type={asset.asset_type}, guide_name={guide_name}")

    # 避免重复生成：如果该资产已经有记录，就先删掉旧的再重新生成
    db.query(CheckRecord).filter(CheckRecord.asset_id == asset.id).delete()

    created_count = 0

    for template in templates:
        record = CheckRecord(
            project_id=asset.project_id,
            asset_id=asset.id,
            template_id=template.id,
            result_record=None,
            compliance_status=None,
            record_remark=None,
            ai_suggestion=None,
        )
        db.add(record)
        created_count += 1

    db.commit()
    return created_count
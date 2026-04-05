from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from openai import OpenAI

from app.core.database import get_db
from app.models.check_record import CheckRecord
from app.models.check_template import CheckTemplate
from app.models.asset import Asset

import json
import re
from typing import List

router = APIRouter(prefix="/ai", tags=["AI辅助"])

class AiPriorityAdviceResponse(BaseModel):
    advice: str
@router.get("/priority/asset/{asset_id}", response_model=AiPriorityAdviceResponse)
def generate_priority_ai_advice(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    rows = (
        db.query(CheckRecord, CheckTemplate)
        .join(CheckTemplate, CheckRecord.template_id == CheckTemplate.id)
        .filter(CheckRecord.asset_id == asset_id)
        .all()
    )

    priority_rows = []
    for record, template in rows:
        if record.compliance_status not in ["partial", "non_compliant"]:
            continue

        score = compliance_to_score(record.compliance_status)
        weight = safe_float(template.weight)
        priority_score = round((5 - score) * weight, 2)

        priority_rows.append({
            "seq_no": template.seq_no,
            "control_item": template.control_item or "",
            "compliance_status": record.compliance_status,
            "weight": weight,
            "priority_score": priority_score,
        })

    if not priority_rows:
        return AiPriorityAdviceResponse(advice="")

    def seq_sort_key(item):
        try:
            return int(item["seq_no"])
        except Exception:
            return 999999

    priority_rows.sort(key=lambda x: (-x["priority_score"], seq_sort_key(x)))
    top_rows = priority_rows[:5]

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="未配置 DASHSCOPE_API_KEY")

    base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name = os.getenv("DASHSCOPE_MODEL", "qwen-plus-latest")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    top_text = "\n".join([
        f"序号：{item['seq_no']}；符合情况：{item['compliance_status']}；权重：{item['weight']}；优先值：{item['priority_score']}；控制项：{item['control_item']}"
        for item in top_rows
    ])

    system_prompt = """
你是等级保护测评辅助系统中的优先级补充说明助手。
你的任务不是重新排序，而是在已有排序结果基础上，补充2到3行简短说明。
不要输出markdown，不要编号，不要分点。
"""

    user_prompt = f"""
请根据以下资产整改优先级结果，生成2到3行简短的补充处理建议。

资产名称：{asset.asset_name or ""}
作业指导书类型：{asset.os_or_db_type or ""}

当前优先级靠前的问题项如下：
{top_text}

要求：
1. 不要推翻已有排序结果；
2. 只做补充说明；
3. 可以提示“同分项中可优先处理整改成本低、见效快的问题”；
4. 语言简洁，控制在2到3行；
5. 不要写成详细整改方案；
6. 直接返回纯文本。
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )

        content = response.choices[0].message.content or ""
        return AiPriorityAdviceResponse(advice=content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 生成失败：{str(e)}")

class AiSuggestionResponse(BaseModel):
    problem_description: str
    possible_causes: str
    rectification_suggestion: str

def extract_json_text(text: str) -> str:
    text = text.strip()

    # 去掉 ```json ... ``` 代码块包裹
    if text.startswith("```"):
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return text.strip()

def parse_ai_response_text(text: str) -> dict:
    text = extract_json_text(text)

    # 先尝试按 JSON 解析
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return {
                "problem_description": str(parsed.get("problem_description", "")).strip(),
                "possible_causes": str(parsed.get("possible_causes", "")).strip(),
                "rectification_suggestion": str(parsed.get("rectification_suggestion", "")).strip(),
            }
    except Exception:
        pass

    # 再兜底解析“字段名：内容”这种普通文本
    patterns = {
        "problem_description": [r"problem_description\s*[：:]\s*(.*?)(?=\n\s*possible_causes\s*[：:]|\n\s*rectification_suggestion\s*[：:]|$)",
                                r"问题描述\s*[：:]\s*(.*?)(?=\n\s*可能原因\s*[：:]|\n\s*整改建议\s*[：:]|$)"],
        "possible_causes": [r"possible_causes\s*[：:]\s*(.*?)(?=\n\s*rectification_suggestion\s*[：:]|$)",
                            r"可能原因\s*[：:]\s*(.*?)(?=\n\s*整改建议\s*[：:]|$)"],
        "rectification_suggestion": [r"rectification_suggestion\s*[：:]\s*(.*)$",
                                      r"整改建议\s*[：:]\s*(.*)$"],
    }

    result = {
        "problem_description": "",
        "possible_causes": "",
        "rectification_suggestion": "",
    }

    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                result[field] = match.group(1).strip()
                break

    if any(result.values()):
        return result

    raise ValueError(f"无法解析 AI 返回内容：{text}")

def compliance_to_score(value):
    if value == "compliant":
        return 5.0
    if value == "partial":
        return 2.5
    if value == "non_compliant":
        return 0.0
    return 0.0


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0

def compliance_to_cn(value: str | None) -> str:
    mapping = {
        "compliant": "符合",
        "partial": "部分符合",
        "non_compliant": "不符合",
        None: "",
        "": "",
    }
    return mapping.get(value, value or "")


@router.get("/record/{record_id}", response_model=AiSuggestionResponse)
def generate_record_ai_suggestion(record_id: int, db: Session = Depends(get_db)):
    record = db.query(CheckRecord).filter(CheckRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="核查记录不存在")

    template = db.query(CheckTemplate).filter(CheckTemplate.id == record.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    asset = db.query(Asset).filter(Asset.id == record.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    if record.compliance_status not in ["partial", "non_compliant"]:
        raise HTTPException(status_code=400, detail="仅“部分符合”或“不符合”记录可生成整改建议")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="未配置 DASHSCOPE_API_KEY")

    base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name = os.getenv("DASHSCOPE_MODEL", "qwen-plus-latest")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    system_prompt = """
你是等级保护测评辅助系统中的整改建议助手。
你的任务是根据单条核查记录，输出规范、简洁、适合写入系统的整改建议。
不要输出 markdown，不要输出标题编号，不要输出多余解释。
"""

    user_prompt = f"""
请基于以下信息，生成整改建议：

作业指导书类型：{asset.os_or_db_type or ""}
控制点：{template.control_point or ""}
控制项：{template.control_item or ""}
检查内容：{template.check_content or ""}
判断标准：{template.judgment_standard or ""}
检查方法：{template.check_method or ""}
推荐值：{template.recommended_value or ""}
模板备注：{template.remark or ""}
结果记录：{record.result_record or ""}
符合情况：{compliance_to_cn(record.compliance_status)}

请严格只返回一个 JSON 对象，不要返回 markdown，不要返回代码块，不要返回额外解释。

JSON 格式如下：
{{
  "problem_description": "一句到两句，概括当前问题",
  "possible_causes": "一句到三句，说明常见原因",
  "rectification_suggestion": "两到四句，给出可执行整改建议"
}}

要求：
- 语气正式
- 尽量贴近等保测评整改语境
- 不要编造具体厂商命令
- 如果结果记录过少，就基于模板字段给出稳妥建议
- 必须返回合法 JSON
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content or ""

        try:
            parsed = parse_ai_response_text(content)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail=f"AI 返回结果无法解析：{content}"
            )

        return AiSuggestionResponse(
            problem_description=parsed.get("problem_description", "").strip(),
            possible_causes=parsed.get("possible_causes", "").strip(),
            rectification_suggestion=parsed.get("rectification_suggestion", "").strip(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 生成失败：{str(e)}")
    
    
from datetime import datetime, timedelta
import hashlib
import hmac
import re
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.asset import Asset
from app.models.check_record import CheckRecord
from app.schemas.user import UserRegister, UserLogin, UserResponse

router = APIRouter(prefix="/users", tags=["用户"])


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    username: str
    password: str


def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="密码长度不能少于8位")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="密码需包含至少一个大写字母")

    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="密码需包含至少一个小写字母")

    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="密码需包含至少一个数字")



def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, hashed_hex = stored_password.split("$", 1)
    except ValueError:
        return False

    test_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    return hmac.compare_digest(test_hash, hashed_hex)


@router.post("/register", response_model=UserResponse)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == data.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")

    validate_password_strength(data.password)

    user = User(
        username=data.username,
        password=hash_password(data.password),
        failed_login_attempts=0,
        lock_until=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=UserResponse)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    now = datetime.now()
    if user.lock_until and user.lock_until > now:
        raise HTTPException(status_code=400, detail="连续输错次数过多，请1分钟后再试")

    if not verify_password(data.password, user.password):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        if user.failed_login_attempts >= 5:
            user.lock_until = now + timedelta(minutes=1)
            user.failed_login_attempts = 0
            db.commit()
            raise HTTPException(status_code=400, detail="连续输错次数过多，请1分钟后再试")

        db.commit()
        raise HTTPException(status_code=400, detail=f"用户名或密码错误，已累计失败{user.failed_login_attempts}次")

    user.failed_login_attempts = 0
    user.lock_until = None
    db.commit()

    return user


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="原密码错误")

    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与原密码相同")

    validate_password_strength(data.new_password)

    user.password = hash_password(data.new_password)
    user.failed_login_attempts = 0
    user.lock_until = None
    db.commit()

    return {"message": "密码修改成功"}



@router.post("/delete-account")
def delete_account(data: DeleteAccountRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="密码错误")

    project_ids = [item.id for item in db.query(Project).filter(Project.user_id == user.id).all()]

    if project_ids:
        asset_ids = [item.id for item in db.query(Asset).filter(Asset.project_id.in_(project_ids)).all()]

        if asset_ids:
            db.query(CheckRecord).filter(CheckRecord.asset_id.in_(asset_ids)).delete(synchronize_session=False)

        db.query(Asset).filter(Asset.project_id.in_(project_ids)).delete(synchronize_session=False)
        db.query(Project).filter(Project.id.in_(project_ids)).delete(synchronize_session=False)

    db.delete(user)
    db.commit()

    return {"message": "账户已注销"}
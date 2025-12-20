from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
from typing import Optional

from .. import models
from ..db import get_db
from ..core.security import get_current_user
from ..schemas import UserOut

router = APIRouter(prefix="/api")

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(name: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if name:
        current_user.name = name
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    return current_user

@router.post("/profile/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Only .jpg, .jpeg, .png allowed")

    static_root = os.path.join(os.path.dirname(__file__), "..", "static")
    static_root = os.path.abspath(static_root)
    os.makedirs(static_root, exist_ok=True)

    filename = f"user_{current_user.id}{ext}"
    path = os.path.join(static_root, filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    current_user.avatar_url = f"/static/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

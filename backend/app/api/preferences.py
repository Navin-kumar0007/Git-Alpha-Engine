from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..core.security import get_current_user
from ..schemas import PreferenceOut, PreferenceUpdate

router = APIRouter(prefix="/api")

@router.get("/preferences", response_model=PreferenceOut)
def get_preferences(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    prefs = current_user.preferences
    if not prefs:
        prefs = models.UserPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs

@router.put("/preferences", response_model=PreferenceOut)
def update_preferences(
    update: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prefs = current_user.preferences
    if not prefs:
        prefs = models.UserPreference(user_id=current_user.id)
        db.add(prefs)
    prefs.theme = update.theme
    prefs.default_tab = update.default_tab
    prefs.risk_profile = update.risk_profile
    db.commit()
    db.refresh(prefs)
    return prefs

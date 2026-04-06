from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.middleware.auth import get_current_user, require_roles

router = APIRouter(prefix="/users", tags=["Users"])


#  List all users (admin only) 
@router.get("/", response_model=list[schemas.UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return db.query(models.User).all()


#  Get my own profile 
@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


#  Update role (admin only) 
@router.patch("/{user_id}/role", response_model=schemas.UserResponse)
def update_role(
    user_id: str,
    body: schemas.UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = body.role
    db.commit()
    db.refresh(user)
    return user


#  Activate / Deactivate user (admin only) 
@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
def update_status(
    user_id: str,
    body: schemas.UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate yourself")

    user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return user


#  Delete user (admin only) 
@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
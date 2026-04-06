from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app import models, schemas
from app.middleware.auth import get_current_user, require_roles
from datetime import date
from typing import Optional
import uuid

router = APIRouter(prefix="/records", tags=["Financial Records"])


# ── Create ────────────────────────────────────────────
@router.post("/", response_model=schemas.RecordResponse)
def create_record(
    body: schemas.RecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst"))
):
    record = models.FinancialRecord(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        amount=body.amount,
        type=body.type,
        category=body.category,
        date=body.date,
        notes=body.notes
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── List with filters ─────────────────────────────────
@router.get("/", response_model=list[schemas.RecordResponse])
def list_records(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.deleted_at == None
    )

    # admins see all records, others see only their own
    if current_user.role != "admin":
        query = query.filter(models.FinancialRecord.user_id == current_user.id)

    if type:
        query = query.filter(models.FinancialRecord.type == type)
    if category:
        query = query.filter(models.FinancialRecord.category == category)
    if from_date:
        query = query.filter(models.FinancialRecord.date >= from_date)
    if to_date:
        query = query.filter(models.FinancialRecord.date <= to_date)

    offset = (page - 1) * limit
    return query.order_by(models.FinancialRecord.date.desc()).offset(offset).limit(limit).all()


# ── Get one ───────────────────────────────────────────
@router.get("/{record_id}", response_model=schemas.RecordResponse)
def get_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    record = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.id == record_id,
        models.FinancialRecord.deleted_at == None
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # viewers and analysts can only see their own records
    if current_user.role != "admin" and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return record


# ── Update ────────────────────────────────────────────
@router.patch("/{record_id}", response_model=schemas.RecordResponse)
def update_record(
    record_id: str,
    body: schemas.RecordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst"))
):
    record = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.id == record_id,
        models.FinancialRecord.deleted_at == None
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # analysts can only update their own records
    if current_user.role == "analyst" and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # only update fields that were actually sent
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


# ── Soft Delete ───────────────────────────────────────
@router.delete("/{record_id}")
def delete_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    record = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.id == record_id,
        models.FinancialRecord.deleted_at == None
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    from datetime import datetime
    record.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "Record deleted successfully"}
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app import models
from app.middleware.auth import get_current_user, require_roles
from datetime import date
from typing import Optional

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ── Summary (total income, expense, balance) ──────────
@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(
        models.FinancialRecord.type,
        func.sum(models.FinancialRecord.amount).label("total")
    ).filter(
        models.FinancialRecord.deleted_at == None
    )

    if current_user.role != "admin":
        query = query.filter(models.FinancialRecord.user_id == current_user.id)

    results = query.group_by(models.FinancialRecord.type).all()

    summary = {"income": 0, "expense": 0, "balance": 0}
    for row in results:
        summary[row.type] = float(row.total)

    summary["balance"] = summary["income"] - summary["expense"]
    return summary


# ── Category breakdown ────────────────────────────────
@router.get("/categories")
def get_category_breakdown(
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(
        models.FinancialRecord.category,
        models.FinancialRecord.type,
        func.sum(models.FinancialRecord.amount).label("total")
    ).filter(
        models.FinancialRecord.deleted_at == None
    )

    if current_user.role != "admin":
        query = query.filter(models.FinancialRecord.user_id == current_user.id)

    if type:
        query = query.filter(models.FinancialRecord.type == type)

    results = query.group_by(
        models.FinancialRecord.category,
        models.FinancialRecord.type
    ).all()

    return [
        {"category": r.category, "type": r.type, "total": float(r.total)}
        for r in results
    ]


# ── Monthly trends ────────────────────────────────────
@router.get("/trends")
def get_monthly_trends(
    year: int = Query(default=date.today().year),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("analyst", "admin"))
):
    query = db.query(
        extract("month", models.FinancialRecord.date).label("month"),
        models.FinancialRecord.type,
        func.sum(models.FinancialRecord.amount).label("total")
    ).filter(
        models.FinancialRecord.deleted_at == None,
        extract("year", models.FinancialRecord.date) == year
    )

    if current_user.role != "admin":
        query = query.filter(models.FinancialRecord.user_id == current_user.id)

    results = query.group_by(
        extract("month", models.FinancialRecord.date),
        models.FinancialRecord.type
    ).order_by("month").all()

    # Build a clean month by month structure
    trends = {}
    for row in results:
        month = int(row.month)
        if month not in trends:
            trends[month] = {"month": month, "income": 0, "expense": 0}
        trends[month][row.type] = float(row.total)

    return list(trends.values())


# ── Recent activity ───────────────────────────────────
@router.get("/recent")
def get_recent(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.deleted_at == None
    )

    if current_user.role != "admin":
        query = query.filter(models.FinancialRecord.user_id == current_user.id)

    records = query.order_by(
        models.FinancialRecord.created_at.desc()
    ).limit(limit).all()

    return records
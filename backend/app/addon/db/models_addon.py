from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.db.base import Base

class AddonCohort(Base):
    __tablename__ = "addon_cohorts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    origin_addr: Mapped[str] = mapped_column(String(255))
    chain: Mapped[str] = mapped_column(String(50))
    asset: Mapped[str] = mapped_column(String(50))
    n_members: Mapped[int] = mapped_column(Integer)
    s_total: Mapped[float] = mapped_column(Float)
    amount_median: Mapped[float] = mapped_column(Float)
    amount_cv: Mapped[float] = mapped_column(Float)
    t_start: Mapped[datetime] = mapped_column(DateTime)
    t_end: Mapped[datetime] = mapped_column(DateTime)
    layer: Mapped[int] = mapped_column(Integer)
    truncated: Mapped[bool] = mapped_column(Boolean)
    kind: Mapped[str] = mapped_column(String(50))

class AddonCohortMember(Base):
    __tablename__ = "addon_cohort_members"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("addon_cohorts.id"))
    address: Mapped[str] = mapped_column(String(255), index=True)
    received_amount: Mapped[float] = mapped_column(Float)
    ts: Mapped[datetime] = mapped_column(DateTime)
    # Note: Alembic / manual indices on (cohort_id, address) will be generated.

class AddonCohortEdge(Base):
    __tablename__ = "addon_cohort_edges"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("addon_cohorts.id"))
    dst_ref: Mapped[str] = mapped_column(String(255))
    dst_kind: Mapped[str] = mapped_column(String(50))
    votes: Mapped[int] = mapped_column(Integer)
    value: Mapped[float] = mapped_column(Float)
    coverage_value: Mapped[float] = mapped_column(Float)
    coverage_breadth: Mapped[float] = mapped_column(Float)
    time_compactness: Mapped[float] = mapped_column(Float)
    conservation_error: Mapped[float] = mapped_column(Float)
    score: Mapped[float] = mapped_column(Float)
    tier: Mapped[str] = mapped_column(String(50))
    verified: Mapped[bool] = mapped_column(Boolean)

class AddonMassSnapshot(Base):
    __tablename__ = "addon_mass_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    t: Mapped[datetime] = mapped_column(DateTime)
    position_ref: Mapped[str] = mapped_column(String(255))
    kind: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    value_est: Mapped[float] = mapped_column(Float)
    value_lo: Mapped[float] = mapped_column(Float)
    value_hi: Mapped[float] = mapped_column(Float)

class AddonPlan(Base):
    __tablename__ = "addon_plans"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    t: Mapped[datetime] = mapped_column(DateTime)
    ev_total: Mapped[float] = mapped_column(Float)
    ev_lo: Mapped[float] = mapped_column(Float)
    ev_hi: Mapped[float] = mapped_column(Float)
    params_hash: Mapped[str] = mapped_column(String(255))
    illustrative_priors: Mapped[bool] = mapped_column(Boolean)

class AddonPlanAction(Base):
    __tablename__ = "addon_plan_actions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("addon_plans.id"))
    rank: Mapped[int] = mapped_column(Integer)
    lever: Mapped[str] = mapped_column(String(100))
    target_ref: Mapped[str] = mapped_column(String(255))
    expected_secured: Mapped[float] = mapped_column(Float)
    lo: Mapped[float] = mapped_column(Float)
    hi: Mapped[float] = mapped_column(Float)
    deadline: Mapped[datetime] = mapped_column(DateTime)
    eta_hours: Mapped[float] = mapped_column(Float)
    prereqs_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    doc_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class AddonWatch(Base):
    __tablename__ = "addon_watches"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    position_ref: Mapped[str] = mapped_column(String(255))
    hazard: Mapped[float] = mapped_column(Float)
    next_check: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50))

class AddonActionOutcome(Base):
    __tablename__ = "addon_action_outcomes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_action_id: Mapped[int] = mapped_column(ForeignKey("addon_plan_actions.id"))
    outcome: Mapped[str] = mapped_column(String(50))
    ts: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

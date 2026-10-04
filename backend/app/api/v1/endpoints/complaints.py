import csv
import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.models import AuditLog, Case, Complaint, Job, User
from app.db.session import get_db

router = APIRouter()

class ComplaintCreate(BaseModel):
    external_ref: Optional[str] = None
    source: str = "api"
    chain: str
    address: str
    reported_amount: float
    reported_asset: str
    reported_at: datetime

class ComplaintResponse(BaseModel):
    id: int
    external_ref: Optional[str]
    status: str

    class Config:
        orm_mode = True

@router.post("", response_model=ComplaintResponse)
async def create_complaint(
    complaint_in: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Deduplicate check
    stmt = select(Complaint).where(Complaint.chain == complaint_in.chain, Complaint.address == complaint_in.address)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    complaint = Complaint(
        external_ref=complaint_in.external_ref,
        source=complaint_in.source,
        chain=complaint_in.chain,
        address=complaint_in.address,
        reported_amount=complaint_in.reported_amount,
        reported_asset=complaint_in.reported_asset,
        reported_at=complaint_in.reported_at,
        received_at=datetime.now(timezone.utc),
        status="pending"
    )
    session.add(complaint)
    await session.flush()

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_COMPLAINT",
        entity="COMPLAINT",
        entity_id=str(complaint.id),
        detail_json={"chain": complaint.chain, "address": complaint.address}
    )
    session.add(audit)

    # Auto-create Case and Job
    case = Case(
        complaint_id=complaint.id,
        owner_id=current_user.id,
        status="queued",
        mode="live",
        config_hash="default"
    )
    session.add(case)
    await session.flush()

    job = Job(
        case_id=case.id,
        kind="TRACE",
        status="pending",
        progress=0,
        payload_json={"chain": complaint.chain, "address": complaint.address}
    )
    session.add(job)

    await session.commit()
    await session.refresh(complaint)

    return complaint

@router.post("/bulk")
async def bulk_import_complaints(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Accepts CSV format with columns:
    external_ref,source,chain,address,reported_amount,reported_asset,reported_at
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV is supported currently.")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    results = {"imported": 0, "errors": [], "duplicates": 0}

    for row_num, row in enumerate(reader, start=2):
        try:
            # Basic validation
            chain = row["chain"]
            address = row["address"]

            stmt = select(Complaint).where(Complaint.chain == chain, Complaint.address == address)
            res = await session.execute(stmt)
            if res.scalar_one_or_none():
                results["duplicates"] += 1
                continue

            complaint = Complaint(
                external_ref=row.get("external_ref"),
                source=row.get("source", "csv"),
                chain=chain,
                address=address,
                reported_amount=float(row["reported_amount"]),
                reported_asset=row["reported_asset"],
                reported_at=datetime.fromisoformat(row["reported_at"].replace("Z", "+00:00")),
                received_at=datetime.now(timezone.utc),
                status="pending"
            )
            session.add(complaint)
            await session.flush()

            case = Case(
                complaint_id=complaint.id,
                owner_id=current_user.id,
                status="queued",
                mode="live",
                config_hash="default"
            )
            session.add(case)
            await session.flush()

            job = Job(
                case_id=case.id,
                kind="TRACE",
                status="pending",
                progress=0,
                payload_json={"chain": chain, "address": address}
            )
            session.add(job)

            results["imported"] += 1

        except Exception as e:
            results["errors"].append({"row": row_num, "error": str(e)})

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="BULK_IMPORT_COMPLAINTS",
        entity="COMPLAINT",
        detail_json=results
    )
    session.add(audit)

    await session.commit()
    return results

@router.get("")
async def list_complaints(
    skip: int = 0, limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Complaint).offset(skip).limit(limit)
    res = await session.execute(stmt)
    return res.scalars().all()

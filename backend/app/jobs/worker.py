import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.db.models import Case, Job
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def process_job(job_id: int):
    async with AsyncSessionLocal() as session:
        # Mark as running
        stmt = update(Job).where(Job.id == job_id).values(
            status="running", started_at=datetime.now(timezone.utc)
        )
        await session.execute(stmt)
        await session.commit()

        try:
            # Simulate pipeline execution
            logger.info(f"Processing job {job_id}")
            await asyncio.sleep(2) # Mock trace time

            # Mark completed
            stmt_ok = update(Job).where(Job.id == job_id).values(
                status="completed", progress=100, finished_at=datetime.now(timezone.utc)
            )
            await session.execute(stmt_ok)

            # Update case status
            # fetch case_id
            res = await session.execute(select(Job).where(Job.id == job_id))
            job = res.scalar_one_or_none()
            if job:
                stmt_case = update(Case).where(Case.id == job.case_id).values(status="completed")
                await session.execute(stmt_case)

            await session.commit()
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            stmt_fail = update(Job).where(Job.id == job_id).values(
                status="failed", error=str(e), finished_at=datetime.now(timezone.utc)
            )
            await session.execute(stmt_fail)
            await session.commit()


async def run_worker():
    """Background polling worker for simple jobs queue."""
    logger.info("Started background job worker")
    while True:
        try:
            async with AsyncSessionLocal() as session:
                # Find pending jobs
                stmt = select(Job).where(Job.status == "pending").limit(5)
                res = await session.execute(stmt)
                pending_jobs = res.scalars().all()

                for job in pending_jobs:
                    asyncio.create_task(process_job(job.id))

            await asyncio.sleep(5) # Poll every 5s
        except asyncio.CancelledError:
            logger.info("Worker cancelled")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(5)

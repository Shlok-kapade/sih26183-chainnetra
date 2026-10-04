import hashlib
import json
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RawResponse


class ResponseCache:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cached_response(self, provider: str, url: str, params: Dict[str, Any]) -> Optional[str]:
        params_json = json.dumps(params, sort_keys=True)
        stmt = select(RawResponse).where(
            RawResponse.provider == provider,
            RawResponse.url == url,
            RawResponse.params_json == params_json
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            return record.body
        return None

    async def store_response(self, provider: str, url: str, params: Dict[str, Any], status: int, body: str, case_id: Optional[int] = None) -> RawResponse:
        params_json = json.dumps(params, sort_keys=True)
        body_sha256 = hashlib.sha256(body.encode('utf-8')).hexdigest()

        # Check if exists to never mutate
        stmt = select(RawResponse).where(
            RawResponse.provider == provider,
            RawResponse.url == url,
            RawResponse.params_json == params_json
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        new_record = RawResponse(
            provider=provider,
            url=url,
            params_json=params_json,
            status=status,
            body=body,
            sha256=body_sha256,
            case_id=case_id
        )
        self.session.add(new_record)
        await self.session.commit()
        await self.session.refresh(new_record)
        return new_record

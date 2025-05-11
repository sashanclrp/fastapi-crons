from fastapi import APIRouter
from .state import SQLiteStateBackend
from .scheduler import Crons
import asyncio

router = APIRouter()

_crons: Crons = None

async def get_all_jobs():
    if not _crons:
        return []
    jobs = _crons.get_jobs()
    backend = _crons.state_backend
    result = []
    for job in jobs:
        last_run = await backend.get_last_run(job.name)
        result.append({
            "name": job.name,
            "expr": job.expr,
            "tags": job.tags,
            "last_run": last_run,
            "next_run": job.next_run.isoformat()
        })
    return result

@router.get("/crons")
async def list_cron_jobs():
    return await get_all_jobs()

@router.on_event("startup")
def bind_scheduler_instance():
    global _crons
    pass
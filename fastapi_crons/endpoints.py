from fastapi import APIRouter
from .state import SQLiteStateBackend
from .scheduler import Crons
import asyncio
from datetime import datetime
import inspect

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
            "next_run": job.next_run.isoformat(),
            "hooks": {
                "before_run": len(job.before_run_hooks),
                "after_run": len(job.after_run_hooks),
                "on_error": len(job.on_error_hooks)
            }
        })
    return result

@router.get("/crons")
async def list_cron_jobs():
    return await get_all_jobs()

@router.on_event("startup")
def bind_scheduler_instance():
    global _crons
    from .scheduler import Crons
    _crons = Crons()

async def execute_hook(hook, job_name: str, context: dict):
    """Execute a hook function, handling both sync and async hooks."""
    try:
        if inspect.iscoroutinefunction(hook):
            await hook(job_name, context)
        else:
            await asyncio.to_thread(hook, job_name, context)
    except Exception as e:
        print(f"[Error][Hook][{job_name}] {e}")

@router.post("/crons/{job_name}/run")
async def run_job(job_name: str):
    if not _crons:
        return {"error": "Scheduler not initialized"}
    
    for job in _crons.get_jobs():
        if job.name == job_name:
            # Create context for hooks
            context = {
                "job_name": job.name,
                "manual_trigger": True,
                "trigger_time": datetime.now().isoformat(),
                "tags": job.tags,
                "expr": job.expr,
            }
            
            # Execute before_run hooks
            for hook in job.before_run_hooks:
                await execute_hook(hook, job.name, context)
                
            start_time = datetime.now()
            error = None
            
            try:
                if asyncio.iscoroutinefunction(job.func):
                    result = await job.func()
                else:
                    result = await asyncio.to_thread(job.func)
                
                job.last_run = datetime.now()
                await _crons.state_backend.set_last_run(job.name, job.last_run)
                
                # Update context with execution details
                context.update({
                    "success": True,
                    "start_time": start_time.isoformat(),
                    "end_time": job.last_run.isoformat(),
                    "duration": (job.last_run - start_time).total_seconds(),
                    "result": result
                })
                
                # Execute after_run hooks
                for hook in job.after_run_hooks:
                    await execute_hook(hook, job.name, context)
                    
                return {
                    "status": "success", 
                    "message": f"Job '{job_name}' executed successfully",
                    "execution_time": (job.last_run - start_time).total_seconds()
                }
                
            except Exception as e:
                error = str(e)
                
                # Update context with error details
                context.update({
                    "success": False,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "error": error
                })
                
                # Execute on_error hooks
                for hook in job.on_error_hooks:
                    await execute_hook(hook, job.name, context)
                    
                return {"status": "error", "message": error}
    
    return {"status": "error", "message": f"Job '{job_name}' not found"}

def get_cron_router():
    return router

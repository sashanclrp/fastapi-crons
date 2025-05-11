import asyncio
import inspect
from datetime import datetime
from .state import SQLiteStateBackend
from .job import CronJob, HookFunc

async def execute_hook(hook: HookFunc, job_name: str, context: dict):
    """Execute a hook function, handling both sync and async hooks."""
    try:
        if inspect.iscoroutinefunction(hook):
            await hook(job_name, context)
        else:
            await asyncio.to_thread(hook, job_name, context)
    except Exception as e:
        print(f"[Error][Hook][{job_name}] {e}")

async def run_job_loop(job: CronJob, state: SQLiteStateBackend):
    while True:
        now = datetime.now()
        seconds = (job.next_run - now).total_seconds()
        await asyncio.sleep(max(0, seconds))

        # Create context for hooks
        context = {
            "job_name": job.name,
            "scheduled_time": job.next_run,
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
            await state.set_last_run(job.name, job.last_run)
            
            # Update context with execution details
            context.update({
                "success": True,
                "start_time": start_time,
                "end_time": job.last_run,
                "duration": (job.last_run - start_time).total_seconds(),
                "result": result
            })
            
            # Execute after_run hooks
            for hook in job.after_run_hooks:
                await execute_hook(hook, job.name, context)
                
        except Exception as e:
            error = str(e)
            print(f"[Error][{job.name}] {e}")
            
            # Update context with error details
            context.update({
                "success": False,
                "start_time": start_time,
                "end_time": datetime.now(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "error": error
            })
            
            # Execute on_error hooks
            for hook in job.on_error_hooks:
                await execute_hook(hook, job.name, context)

        job.update_next_run()

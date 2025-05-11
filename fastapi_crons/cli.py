import typer
import asyncio
import inspect
from .state import SQLiteStateBackend
from datetime import datetime

cli = typer.Typer()
state = SQLiteStateBackend()

@cli.command()
def list():
    """List all jobs and last run time."""
    async def run():
        print("Registered jobs:")
        jobs = await state.get_all_jobs()
        if not jobs:
            print("  No jobs registered")
            return
        
        for job_name, last_run in jobs:
            last_run_str = last_run if last_run else "Never run"
            print(f"  - {job_name}: Last run: {last_run_str}")
    
    asyncio.run(run())

async def execute_hook(hook, job_name: str, context: dict):
    """Execute a hook function, handling both sync and async hooks."""
    try:
        if inspect.iscoroutinefunction(hook):
            await hook(job_name, context)
        else:
            await asyncio.to_thread(hook, job_name, context)
    except Exception as e:
        print(f"[Error][Hook][{job_name}] {e}")

@cli.command()
def run_job(name: str):
    """Manually run a job (name must match)."""
    async def run():
        from .scheduler import Crons
        crons = Crons(state_backend=state)
        jobs = crons.get_jobs()
        
        for job in jobs:
            if job.name == name:
                print(f"Running job '{name}' manually...")
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
                    await state.set_last_run(job.name, job.last_run)
                    
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
                        
                    print(f"Job '{name}' completed successfully")
                    return
                    
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
                        
                    print(f"Error running job '{name}': {e}")
                    return
        
        print(f"No job found with name '{name}'")
    
    asyncio.run(run())

if __name__ == "__main__":
    cli()

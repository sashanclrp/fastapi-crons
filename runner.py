import asyncio
from datetime import datetime
from .state import SQLiteStateBackend
from .job import CronJob

async def run_job_loop(job: CronJob, state: SQLiteStateBackend):
    while True:
        now = datetime.now()
        seconds = (job.next_run - now).total_seconds()
        await asyncio.sleep(max(0, seconds))

        try:
            if asyncio.iscoroutinefunction(job.func):
                await job.func()
            else:
                await asyncio.to_thread(job.func)

            job.last_run = datetime.now()
            await state.set_last_run(job.name, job.last_run)
        except Exception as e:
            print(f"[Error][{job.name}] {e}")

        job.update_next_run()

import asyncio
from typing import Callable, List, Optional
from .job import CronJob
from .state import SQLiteStateBackend
from .runner import run_job_loop

class Crons:
    def __init__(self, app=None, state_backend: Optional[SQLiteStateBackend] = None):
        self.jobs: List[CronJob] = []
        self.state_backend = state_backend or SQLiteStateBackend()
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.on_event("startup")
        async def startup():
            for job in self.jobs:
                asyncio.create_task(run_job_loop(job, self.state_backend))

    def cron(self, expr: str, *, name=None, tags=None):
        def wrapper(func: Callable):
            job = CronJob(func, expr, name=name, tags=tags)
            self.jobs.append(job)
            return func
        return wrapper

    def get_jobs(self):
        return self.jobs
import asyncio
from typing import Callable, List, Optional, Dict, Any
from .job import CronJob, HookFunc
from .state import SQLiteStateBackend
from .runner import run_job_loop

_instance = None

class Crons:
    def __init__(self, app=None, state_backend: Optional[SQLiteStateBackend] = None):
        global _instance
    
        # If this is the first instance, initialize it
        if _instance is None:
            self.jobs: List[CronJob] = []
            self.state_backend = state_backend or SQLiteStateBackend()
            self.app = app
            if app:
                self.init_app(app)
            _instance = self
        # If an instance already exists, use its data
        else:
            self.jobs = _instance.jobs
            self.state_backend = state_backend or _instance.state_backend
            self.app = app or _instance.app
            if app and app != _instance.app:
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
        
    def get_job(self, name: str) -> Optional[CronJob]:
        """Get a job by name."""
        for job in self.jobs:
            if job.name == name:
                return job
        return None
        
    def add_before_run_hook(self, hook: HookFunc, job_name: Optional[str] = None):
        """
        Add a hook to be executed before job runs.
        If job_name is provided, hook is added only to that job.
        Otherwise, hook is added to all jobs.
        """
        if job_name:
            job = self.get_job(job_name)
            if job:
                job.add_before_run_hook(hook)
        else:
            for job in self.jobs:
                job.add_before_run_hook(hook)
        return self
        
    def add_after_run_hook(self, hook: HookFunc, job_name: Optional[str] = None):
        """
        Add a hook to be executed after job runs successfully.
        If job_name is provided, hook is added only to that job.
        Otherwise, hook is added to all jobs.
        """
        if job_name:
            job = self.get_job(job_name)
            if job:
                job.add_after_run_hook(hook)
        else:
            for job in self.jobs:
                job.add_after_run_hook(hook)
        return self
        
    def add_on_error_hook(self, hook: HookFunc, job_name: Optional[str] = None):
        """
        Add a hook to be executed when job fails.
        If job_name is provided, hook is added only to that job.
        Otherwise, hook is added to all jobs.
        """
        if job_name:
            job = self.get_job(job_name)
            if job:
                job.add_on_error_hook(hook)
        else:
            for job in self.jobs:
                job.add_on_error_hook(hook)
        return self

from typing import Callable, Optional, List
from datetime import datetime
from croniter import croniter

class CronJob:
    def __init__(self, func: Callable, expr: str, name: Optional[str] = None, tags: Optional[List[str]] = None):
        self.func = func
        self.expr = expr
        self.name = name or func.__name__
        self.tags = tags or []
        self._cron_iter = croniter(expr, datetime.now())
        self.last_run: Optional[datetime] = None
        self.next_run: datetime = self._cron_iter.get_next(datetime)

    def update_next_run(self):
        self.next_run = self._cron_iter.get_next(datetime)
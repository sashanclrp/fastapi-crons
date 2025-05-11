# FastAPI Crons – Developer Guide

Welcome to the official guide for using `fastapi_crons`, a high-performance, developer-friendly cron scheduling extension for FastAPI. This library enables you to define, monitor, and control scheduled background jobs using simple decorators and provides CLI tools, web-based monitoring, and SQLite-based job tracking.

---

## 🚀 Features

* Native integration with FastAPI using `from fastapi import FastAPI, Crons`
* Define cron jobs with decorators
* Async + sync job support
* SQLite job state persistence
* CLI for listing and managing jobs
* Automatic monitoring endpoint (`/crons`)
* Named jobs, tags, and metadata
* Easy to plug into any FastAPI project

---

## 📦 Installation

```bash
pip install fastapi-crons
```

---

## 🛠️ Quick Start

### 1. Setup FastAPI with Crons

```python
from fastapi import FastAPI
from fastapi_crons import Crons, get_cron_router

app = FastAPI()
crons = Crons(app)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}

app.include_router(get_cron_router())
```

### 2. Define Cron Jobs

```python
@crons.cron("*/5 * * * *", name="print_hello")
def print_hello():
    print("Hello! I run every 5 minutes.")

@crons.cron("0 0 * * *", name="daily_task", tags=["rewards"])
async def run_daily_task():
    # Distribute daily rewards or any async task
    await some_async_function()
```

---

## 🖥️ Cron Monitoring Endpoint

Once included, visit:

```
GET /crons
```

You’ll get a full list of jobs with:

* `name`
* `expr` (cron expression)
* `tags`
* `last_run` (from SQLite)
* `next_run`

---

## 🧩 SQLite Job State Tracking

We use SQLite (via `aiosqlite`) to keep a persistent record of when each job last ran. This allows observability and resilience during restarts.

### Table:

```sql
CREATE TABLE IF NOT EXISTS job_state (
    name TEXT PRIMARY KEY,
    last_run TEXT
);
```

---

## 🧵 Async + Thread Execution

Jobs can be:

* `async def` → run in asyncio loop
* `def` → run safely in background thread using `await asyncio.to_thread(...)`

---

## 🧪 CLI Support

```bash
python -m fastapi_crons.cli list
python -m fastapi_crons.cli run-job --name=job_name
```

> **Note**: CLI registry info will be expanded in later versions.

---

## ⚙️ Architecture Overview

```
FastAPI App
│
├── Crons()
│   ├── Registers decorated jobs
│   ├── Starts background scheduler (async)
│
├── SQLite Backend
│   ├── Tracks last run for each job
│
├── /crons endpoint
│   ├── Shows current job status (with timestamps)
│
└── CLI Tool
    ├── List jobs / Run manually
```

---

## 🧩 Advanced Features (coming soon)

* Distributed locking via Redis
* Retry policies
* Manual run triggers via HTTP
* Admin dashboard with metrics

---

## 🧠 Contributing

We welcome PRs and suggestions! If you’d like this added to FastAPI officially, fork the repo, polish it, and submit to FastAPI with a clear integration proposal.

---

## 🛡️ Error Handling

* Each job has an isolated error handler
* Errors are printed and don't block scheduler
* Future: Add error logging / alert hooks

---

## 📄 License

[Licence][/LICENSE.txt]

---

## 💬 Credits

Made with ❤️ by Mehar Umar. Designed to give developers freedom, flexibility, and control when building production-grade FastAPI apps.

---

Need help? Reach out or open an issue on GitHub!
[Email][mailto:contact@meharumar.codes]

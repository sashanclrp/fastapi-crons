import typer
import asyncio
from .state import SQLiteStateBackend

cli = typer.Typer()
state = SQLiteStateBackend()

@cli.command()
def list():
    """List all jobs and last run time."""
    async def run():
        print("Registered jobs:")
        # TODO: Replace this with actual job registry info
    asyncio.run(run())

@cli.command()
def run_job(name: str):
    """Manually run a job (name must match)."""
    print(f"Running job '{name}' manually (not yet implemented).")

if __name__ == "__main__":
    cli()
import asyncio
from arq import run_worker
from worker import WorkerSettings
from utils import configure_logging

configure_logging()

def main():
    asyncio.run(run_worker(WorkerSettings))

if __name__ == "__main__":
    main()

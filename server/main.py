from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
import uvicorn

from .mission_scheduler import check_and_fire_missions
from .routers import drones, missions, schedules


async def periodic_task():
    while True:
        await check_and_fire_missions()
        await asyncio.sleep(120)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(periodic_task())
    try:
        yield
    finally:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

app.include_router(drones.router)
app.include_router(schedules.router)
app.include_router(missions.router)

# TODO: figure how how to extract the db data using models


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)

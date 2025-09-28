from fastapi import FastAPI, Depends, HTTPException, Request, status, BackgroundTasks
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
import uvicorn
import time
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import httpx

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache


scheduler = AsyncIOScheduler()


def my_task():
    print(f"task executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('**********application startup**********')
    # scheduler.add_job(my_task, IntervalTrigger(seconds=2))
    # scheduler.start()
    yield
    # scheduler.shutdown()
    print('**********application shutdown**********')


app = FastAPI(
    title="Todo App API",
    description="A powerful and simple API for managing tasks with FastAPI and PostgreSQL.",
    version="1.0.0",
    contact={
        "name": "Amin Khaleghi",
        "url": "https://yourwebsite.com",
        "email": "aminkhaleghi@gamil.com",
    },
    license_info={
        "name": "MIT License",
    },
    lifespan=lifespan,
)

app.include_router(tasks_routes, prefix="")
app.include_router(users_routes, prefix="")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# origins = [
#     "http://127.0.1:5500/",
#     "http://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    error_response = {
        "error": True,
        "status_code": exc.status_code,
        "detail": str(exc.detail),
    }
    return JSONResponse(status_code=exc.status_code, content=error_response)


@app.exception_handler(RequestValidationError)
async def http_exception_handler(request: Request, exc):
    error_response = {
        "error": True,
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "detail": "there was a problem with your form request",
        "content": exc.errors(),
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response)


task_counter = 1


def start_task(task_id):
    print(f"doing task {task_id}")
    time.sleep(random.randint(3, 10))
    print(f"done task {task_id}")


@app.get("/init-task", status_code=status.HTTP_200_OK)
async def initiate_task(background_tasks: BackgroundTasks):
    global task_counter
    background_tasks.add_task(start_task, task_id=task_counter)
    task_counter += 1
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": f"task {task_counter} done."})


cache_backend = InMemoryBackend()
FastAPICache.init(cache_backend)

async def request_current_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forcast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m, relative_humidity_2m",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        data = response.json()
        current_weather = data.get("current", {})
        return current_weather
    else:
        return None

# @app.get("/fetch-current-weather", status_code=status.HTTP_200_OK)
# @cache(5)
# async def fetch_current_weather(latitude: float = 40.7128, longitude: float = -74.0060):
#     current_weather = await request_current_weather(latitude, longitude)
#     if current_weather:
#         return JSONResponse(status_code=status.HTTP_200_OK, content={"current_weather": current_weather})
#     else:
#         return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "failed to fetch current weather."})


@app.get("/fetch-current-weather", status_code=status.HTTP_200_OK)
@cache(5)
async def fetch_current_weather(latitude: float = 40.7128, longitude: float = -74.0060):
    cache_key = f"weather-{latitude}-{longitude}"
    cache_data = await cache_backend.get(cache_key)
    if cache_data:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"current_weather": cache_data})

    current_weather = await request_current_weather(latitude, longitude)
    if current_weather:
        await cache_backend.set(cache_key, current_weather, 10)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"current_weather": current_weather})
    else:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "failed to fetch current weather."})


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True, reload_delay=500)

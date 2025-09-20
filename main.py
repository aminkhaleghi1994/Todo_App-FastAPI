from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
import uvicorn
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('**********application startup**********')
    yield
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

app.include_router(tasks_routes, prefix="/api/v1")


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



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True, reload_delay=500)

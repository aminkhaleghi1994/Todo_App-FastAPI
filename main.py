from fastapi import FastAPI
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
import uvicorn


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


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True, reload_delay=500)

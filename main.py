from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
import uvicorn
from auth.basic_auth import get_current_username
from users.models import UserModel
from fastapi.security import APIKeyHeader, APIKeyQuery



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

app.include_router(tasks_routes)
app.include_router(users_routes)


header_scheme = APIKeyHeader(name="x-key")
@app.get("/header_scheme/")
async def read_items(api_key: str = Depends(header_scheme)):
    print(api_key)
    return {"api_key": api_key}


query_scheme = APIKeyQuery(name="api_key")
@app.get("/query_scheme/")
async def read_items(api_key: str = Depends(query_scheme)):
    return {"api_key": api_key}


@app.get("/public")
async def public_rout():
    return {"detail": "This Is A Public Route"}


@app.get("/private")
async def private_rout(user: UserModel = Depends(get_current_username)):
    return {"detail": "This Is A Private Route"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True, reload_delay=500)

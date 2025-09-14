from fastapi import FastAPI, Depends, Response, Request
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
import uvicorn
from auth.basic_auth import get_current_username as basic_auth
from auth.bearer_auth import get_current_username as bearer_auth
from auth.jwt_auth import get_authenticated_user as jwt_auth
from users.models import UserModel, TokenModel
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


@app.get("/public")
async def public_rout():
    return {"detail": "This Is A Public Route"}


@app.get("/private")
async def private_rout(user: UserModel = Depends(jwt_auth)):
    return {"detail": "This Is A Private Route"}


@app.get("/set-cookie")
async def set_cookie(response: Response):
    response.set_cookie(key="Test", value="Somthing <PASSWORD>")
    return {
        "message": "Cookie has Been Set Successfully",
    }


@app.get("/set-cookie")
async def get_cookie(request: Request):
    
    return {
        "message": "Cookie has Been Set Successfully",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True, reload_delay=500)

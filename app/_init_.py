from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ServiceDesk Plus", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="super-secret-session-key-change-me")

@app.get("/")
def read_root():
    return RedirectResponse(url="/auth/login")

app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
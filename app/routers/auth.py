from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from app.database import get_db
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["Auth"])
templates = Jinja2Templates(directory="template")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
async def register_user(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        phone_number: str = Form(None),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Паролі не співпадають!"}
        )

    user_exists = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if user_exists:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Користувач з таким логіном або Email вже існує!"}
        )

    new_user = User(
        username=username,
        email=email,
        phone_number=phone_number,
        role=UserRole.CLIENT
    )
    new_user.set_password(password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login")
async def login_user(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not check_password_hash(user.hashed_password, password):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Невірний логін або пароль"}
        )

    request.session["user_id"] = user.id
    request.session["user_role"] = user.role.value

    if user.role.value == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    elif user.role.value == "supplier":
        return RedirectResponse(url="/supplier/dashboard", status_code=303)
    else:
        return RedirectResponse(url="/client/dashboard", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
import os
import shutil
import uuid
import httpx
from datetime import datetime
import weasyprint

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.models.note import Note
from app.models.message import Message

load_dotenv()

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="template")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


@router.get("/client/dashboard", response_class=HTMLResponse)
async def client_dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()
    orders = db.query(Order).filter(Order.client_id == user_id).order_by(Order.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="client_dashboard.html",
        context={"user": user, "orders": orders}
    )


@router.post("/client/telegram")
async def save_client_telegram(request: Request, telegram_id: str = Form(...), db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        try:
            user.telegram_id = telegram_id
            db.commit()
        except IntegrityError:
            db.rollback()
    return RedirectResponse(url="/client/dashboard", status_code=303)


@router.get("/client/orders/create", response_class=HTMLResponse)
async def create_order_page(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse(request=request, name="create_order.html")


@router.post("/client/orders/create")
async def create_order(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        deadline_str: str = Form(None),
        photo: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()

    photo_path = None
    if photo and photo.filename:
        file_extension = os.path.splitext(photo.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_location = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_path = f"/uploads/{unique_filename}"

    deadline = None
    if deadline_str:
        deadline = datetime.fromisoformat(deadline_str)

    new_order = Order(
        client_id=user_id,
        title=title,
        description=description,
        photo_path=photo_path,
        deadline=deadline,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.commit()

    return RedirectResponse(url="/client/dashboard", status_code=303)


@router.get("/client/orders/{order_id}/receipt", response_class=HTMLResponse)
async def view_receipt(order_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    order = db.query(Order).filter(Order.id == order_id, Order.client_id == user_id).first()

    if not order or order.status.value != "completed":
        return HTMLResponse("<h1>Талон недоступний. Ремонт ще не завершено.</h1>", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="receipt.html",
        context={"order": order}
    )


@router.get("/client/orders/{order_id}/receipt/pdf")
async def download_receipt_pdf(order_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    order = db.query(Order).filter(Order.id == order_id, Order.client_id == user_id).first()

    if not order or order.status.value != "completed":
        return HTMLResponse("<h1>Талон недоступний.</h1>", status_code=404)

    html_content = templates.get_template("receipt_pdf.html").render({"order": order})
    pdf = weasyprint.HTML(string=html_content).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=talon_{order.id}.pdf"}
    )


@router.post("/orders/{order_id}/chat")
async def send_message(
        order_id: int,
        request: Request,
        text: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    user_role = request.session.get("user_role")

    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return RedirectResponse(url="/", status_code=303)

    new_msg = Message(
        order_id=order_id,
        sender_id=user_id,
        text=text
    )
    db.add(new_msg)
    db.commit()

    sender = db.query(User).filter(User.id == user_id).first()

    if user_role in ["admin", "master"] and order.client.telegram_id:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": order.client.telegram_id, "text": f"💬 <b>Повідомлення від майстра:</b>\n{text}",
                   "parse_mode": "HTML"}
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload)
            except Exception as e:
                print(f"Помилка Telegram: {e}")

    if user_role == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    elif user_role == "supplier":
        return RedirectResponse(url="/supplier/dashboard", status_code=303)
    return RedirectResponse(url="/client/dashboard", status_code=303)


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user_role = request.session.get("user_role")
    if user_role != "admin":
        return RedirectResponse(url="/auth/login", status_code=303)

    user_id = request.session.get("user_id")
    current_user = db.query(User).filter(User.id == user_id).first()
    orders = db.query(Order).order_by(Order.created_at.desc()).all()

    total_orders = len(orders)
    pending_count = sum(1 for o in orders if o.status.value == 'pending')
    in_progress_count = sum(1 for o in orders if o.status.value == 'in_progress')
    completed_count = sum(1 for o in orders if o.status.value == 'completed')

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "orders": orders,
            "current_user": current_user,
            "now": datetime.utcnow(),
            "stats": {
                "total": total_orders,
                "pending": pending_count,
                "in_progress": in_progress_count,
                "completed": completed_count
            }
        }
    )


@router.post("/admin/orders/{order_id}/update")
async def update_order(
        order_id: int,
        request: Request,
        status: str = Form(...),
        admin_reply: str = Form(None),
        warranty: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    user_role = request.session.get("user_role")
    if user_role != "admin":
        return RedirectResponse(url="/auth/login", status_code=303)

    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = OrderStatus(status)
        if admin_reply is not None:
            order.admin_reply = admin_reply

        if warranty and warranty.filename:
            file_extension = os.path.splitext(warranty.filename)[1]
            unique_filename = f"warranty_{uuid.uuid4().hex}{file_extension}"
            file_location = os.path.join(UPLOAD_DIR, unique_filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(warranty.file, buffer)
            order.warranty_path = f"/uploads/{unique_filename}"

        db.commit()

        if order.client.telegram_id:
            status_ukr = {
                "pending": "Чекає на обробку ⏳",
                "in_progress": "В обробці ⚙️",
                "completed": "Завершено ✅"
            }

            text = (
                f"🔔 <b>Оновлення статусу вашої заявки!</b>\n\n"
                f"📝 <b>Заявка:</b> {order.title}\n"
                f"📌 <b>Новий статус:</b> {status_ukr.get(status, status)}\n"
            )
            if admin_reply:
                text += f"\n💬 <b>Відповідь майстра:</b>\n{admin_reply}"

            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": order.client.telegram_id, "text": text, "parse_mode": "HTML"}

            async with httpx.AsyncClient() as client:
                try:
                    await client.post(url, json=payload)
                except Exception as e:
                    print(f"Помилка Telegram: {e}")

    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/admin/orders/{order_id}/delete")
async def delete_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    user_role = request.session.get("user_role")
    if user_role != "admin":
        return RedirectResponse(url="/auth/login", status_code=303)

    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        db.query(Note).filter(Note.order_id == order_id).delete()
        db.query(Message).filter(Message.order_id == order_id).delete()
        db.delete(order)
        db.commit()

    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/admin/orders/{order_id}/notes")
async def add_note(
        order_id: int,
        request: Request,
        text: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    user_role = request.session.get("user_role")

    if user_role not in ["admin", "master", "supplier"]:
        return RedirectResponse(url="/auth/login", status_code=303)

    new_note = Note(
        order_id=order_id,
        author_id=user_id,
        text=text
    )
    db.add(new_note)
    db.commit()

    if user_role == "supplier":
        return RedirectResponse(url="/supplier/dashboard", status_code=303)
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/supplier/dashboard", response_class=HTMLResponse)
async def supplier_dashboard(request: Request, db: Session = Depends(get_db)):
    user_role = request.session.get("user_role")
    if user_role != "supplier":
        return RedirectResponse(url="/auth/login", status_code=303)

    user_id = request.session.get("user_id")
    current_user = db.query(User).filter(User.id == user_id).first()

    orders = db.query(Order).filter(Order.status == OrderStatus.IN_PROGRESS).order_by(Order.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="supplier_dashboard.html",
        context={"orders": orders, "current_user": current_user}
    )
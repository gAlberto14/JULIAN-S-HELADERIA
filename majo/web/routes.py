"""Rutas web. Son delgadas: leen el formulario, llaman al servicio y muestran el resultado."""
from datetime import date
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from majo.config import Settings
from majo.container import Container
from majo.domain.models import PAYMENT_METHODS, User
from majo.web.deps import admin_only, get_container, optional_user, staff
from majo.web.navigation import cat_icon, nav_for

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
templates.env.filters["money"] = lambda v: ("-" if v < 0 else "") + "$" + f"{abs(round(v)):,}".replace(",", ".")
templates.env.filters["cat_icon"] = cat_icon


def page(request: Request, name: str, user: User | None, **ctx) -> HTMLResponse:
    base = {"user": user, "nav": nav_for(user, request.url.path), "msg": request.query_params.get("msg"),
            "toast_kind": request.query_params.get("t")}
    return templates.TemplateResponse(request, name, {**base, **ctx})


def back(url: str, msg: str | None = None, ok: bool = True) -> RedirectResponse:
    """Redirige mostrando un aviso (toast). ok=False lo muestra como error."""
    query = f"?msg={quote(msg)}" + ("" if ok else "&t=err") if msg else ""
    return RedirectResponse(url + query, status_code=303)


# ---------- Público ----------
@router.get("/", response_class=HTMLResponse)
def inicio(request: Request, user=Depends(optional_user)):
    return page(request, "inicio.html", user)


@router.get("/productos", response_class=HTMLResponse)
def menu(request: Request, user=Depends(optional_user), c: Container = Depends(get_container)):
    cats: dict[str, list] = {}
    for p in c.catalog.menu():
        cats.setdefault(p.cat, []).append(p)
    return page(request, "menu.html", user, cats=cats)


@router.get("/terminos", response_class=HTMLResponse)
def terminos(request: Request, user=Depends(optional_user)):
    return page(request, "legal.html", user, kind="terminos")


@router.get("/cookies", response_class=HTMLResponse)
def cookies(request: Request, user=Depends(optional_user)):
    return page(request, "legal.html", user, kind="cookies")


# ---------- Sesión ----------
@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, user=Depends(optional_user)):
    return page(request, "login.html", user, demo=not Settings().use_supabase)


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), c: Container = Depends(get_container)):
    token = c.auth.login(email, password)
    if not token:
        return back("/login", "Correo o contraseña incorrectos.", False)
    res = back("/ventas")
    # En producción (HTTPS detrás del proxy de Render/Railway) la cookie viaja segura.
    res.set_cookie("token", token, httponly=True, secure=request.url.scheme == "https",
                   samesite="lax", max_age=60 * 60 * 8)
    return res


@router.post("/logout")
def logout():
    res = back("/")
    res.delete_cookie("token")
    return res


# ---------- Ventas (mesero y admin) ----------
@router.get("/ventas", response_class=HTMLResponse)
def ventas(request: Request, user=Depends(staff), c: Container = Depends(get_container)):
    return page(request, "ventas.html", user, products=c.catalog.menu(), today=c.sales.today(), methods=PAYMENT_METHODS)


@router.post("/ventas")
async def registrar_venta(request: Request, user=Depends(staff), c: Container = Depends(get_container)):
    form = await request.form()
    qty = {int(k[4:]): int(v or 0) for k, v in form.items() if k.startswith("qty_") and str(v).isdigit()}
    try:
        sale = c.sales.register(qty, str(form.get("pay", "")), user)
    except ValueError as e:
        return back("/ventas", str(e), False)
    return back("/ventas", f"Venta registrada por {sale.total:,.0f} COP".replace(",", "."))


# ---------- Productos (admin) ----------
@router.get("/admin/productos", response_class=HTMLResponse)
def admin_productos(request: Request, editar: int | None = None, user=Depends(admin_only), c: Container = Depends(get_container)):
    return page(request, "admin_productos.html", user, products=c.catalog.all(), editing=c.catalog.get(editar) if editar else None)


@router.post("/admin/productos")
def guardar_producto(name: str = Form(...), cat: str = Form(""), price: float = Form(...), active: str | None = Form(None),
                     id: str = Form(""), user=Depends(admin_only), c: Container = Depends(get_container)):
    try:
        c.catalog.save(name, cat, price, active is not None, int(id) if id else None)
    except ValueError as e:
        return back("/admin/productos", str(e), False)
    return back("/admin/productos", "Producto guardado.")


@router.post("/admin/productos/{pid}/estado")
def cambiar_estado(pid: int, user=Depends(admin_only), c: Container = Depends(get_container)):
    p = c.catalog.toggle(pid)
    return back("/admin/productos", f"«{p.name}» ahora está {'visible' if p.active else 'oculto'}." if p else "Producto no encontrado.", bool(p))


@router.post("/admin/productos/{pid}/borrar")
def borrar_producto(pid: int, user=Depends(admin_only), c: Container = Depends(get_container)):
    c.catalog.delete(pid)
    return back("/admin/productos", "Producto borrado.")


# ---------- Reportes y contabilidad (admin) ----------
@router.get("/reportes", response_class=HTMLResponse)
def reportes(request: Request, dias: int = 7, user=Depends(admin_only), c: Container = Depends(get_container)):
    return page(request, "reportes.html", user, r=c.reports.summary(dias or None), dias=dias)


@router.get("/conta", response_class=HTMLResponse)
def conta(request: Request, user=Depends(admin_only), c: Container = Depends(get_container)):
    return page(request, "conta.html", user, ledger=c.accounting.ledger(), today=date.today().isoformat())


@router.post("/conta/gasto")
def nuevo_gasto(concept: str = Form(...), amount: float = Form(...), when: date = Form(...),
                user=Depends(admin_only), c: Container = Depends(get_container)):
    try:
        c.accounting.add_expense(concept, amount, when)
    except ValueError as e:
        return back("/conta", str(e), False)
    return back("/conta", "Gasto guardado.")


@router.post("/conta/gasto/{eid}/borrar")
def borrar_gasto(eid: int, user=Depends(admin_only), c: Container = Depends(get_container)):
    c.accounting.delete_expense(eid)
    return back("/conta", "Gasto borrado.")

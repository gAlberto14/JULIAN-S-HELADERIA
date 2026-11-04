"""Pruebas de la interfaz: páginas, permisos por rol, navegación y componentes."""
import pytest
from fastapi.testclient import TestClient

from majo.domain.models import User
from majo.main import app
from majo.web.navigation import cat_icon, nav_for


def client(email=None, pw=None):
    c = TestClient(app, follow_redirects=True)
    if email:
        c.post("/login", data={"email": email, "password": pw})
    return c


PUBLIC = ["/", "/productos", "/login", "/terminos", "/cookies"]
ADMIN = ["/ventas", "/admin/productos", "/admin/productos?editar=1", "/reportes", "/reportes?dias=0", "/conta"]


@pytest.mark.parametrize("url", PUBLIC)
def test_paginas_publicas(url):
    r = client().get(url)
    assert r.status_code == 200 and "majö" in r.text and "tabbar" in r.text


def test_admin_ve_todas_las_paginas():
    c = client("admin@majo.co", "admin123")
    for url in ADMIN:
        assert c.get(url).status_code == 200, url


def test_mesero_solo_ventas_y_no_ve_menu_admin():
    c = client("mesero@majo.co", "mesero123")
    assert c.get("/ventas").status_code == 200
    assert c.get("/reportes").status_code == 403
    assert "/reportes" not in c.get("/ventas").text


def test_sin_sesion_redirige_a_login():
    r = client().get("/ventas")
    assert str(r.url).endswith("/login")


def test_pos_muestra_productos_con_stepper_y_total():
    html = client("mesero@majo.co", "mesero123").get("/ventas").text
    assert 'id="pos"' in html and "stepper" in html and 'id="sellBtn"' in html and 'name="qty_1"' in html


def test_flujo_venta_y_toast_de_exito():
    c = client("admin@majo.co", "admin123")
    r = c.post("/ventas", data={"qty_1": "2", "pay": "Efectivo"})
    assert "Venta registrada" in r.text and 'class="toast "' in r.text
    assert "$12.000" in c.get("/ventas").text


def test_error_se_muestra_como_toast_de_error():
    r = client("admin@majo.co", "admin123").post("/ventas", data={"pay": "Efectivo"})
    assert "toast bad" in r.text


def test_estado_producto_y_reporte_vacio_no_rompen():
    c = client("admin@majo.co", "admin123")
    assert "ahora está oculto" in c.post("/admin/productos/2/estado").text
    assert "Sin ventas" in c.get("/reportes?dias=1").text or "Ticket promedio" in c.get("/reportes?dias=1").text


def test_navegacion_por_rol():
    assert [i["label"] for i in nav_for(None, "/")] == ["Inicio", "Productos"]
    assert len(nav_for(User("1", "A", "admin"), "/")) == 6
    assert [i["active"] for i in nav_for(None, "/productos")] == [False, True]
    assert cat_icon("Helados") == "🍦" and cat_icon("raro") == "🍨"

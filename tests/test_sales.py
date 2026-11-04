"""Pruebas de la lógica de negocio usando repositorios en memoria (sin internet)."""
import pytest

from majo.config import Settings
from majo.container import build_container
from majo.domain.models import User

MESERO = User("2", "Mesero", "mesero")


@pytest.fixture
def c():
    return build_container(Settings(supabase_url="", supabase_anon_key="", supabase_service_key=""))


def test_venta_calcula_total_con_precio_del_catalogo(c):
    sale = c.sales.register({1: 2, 3: 1}, "Efectivo", MESERO)
    assert sale.total == 6000 * 2 + 8500


def test_venta_vacia_falla(c):
    with pytest.raises(ValueError):
        c.sales.register({1: 0}, "Efectivo", MESERO)


def test_balance_resta_gastos(c):
    c.sales.register({1: 1}, "Tarjeta", MESERO)
    from datetime import date
    c.accounting.add_expense("Leche", 2000, date.today())
    assert c.accounting.ledger()["balance"] == 4000


def test_ocultar_producto_lo_saca_del_menu(c):
    assert any(p.id == 1 for p in c.catalog.menu())
    assert c.catalog.toggle(1).active is False
    assert all(p.id != 1 for p in c.catalog.menu())
    assert c.catalog.toggle(1).active is True
    assert c.catalog.toggle(999) is None

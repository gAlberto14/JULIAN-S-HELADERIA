"""Navegación definida en UN solo lugar: para agregar una sección basta una línea en NAV."""
from dataclasses import dataclass

from majo.domain.models import User


@dataclass(frozen=True)
class NavItem:
    href: str
    label: str
    icon: str
    access: str = "public"  # public | staff | admin


NAV = [
    NavItem("/", "Inicio", "🏠"),
    NavItem("/productos", "Productos", "🍦"),
    NavItem("/ventas", "Ventas", "🧾", "staff"),
    NavItem("/admin/productos", "Catálogo", "⚙️", "admin"),
    NavItem("/reportes", "Reportes", "📊", "admin"),
    NavItem("/conta", "Contabilidad", "💰", "admin"),
]

CATEGORY_ICONS = {"helados": "🍦", "conos": "🍨", "copas": "🍧", "extras": "🍒", "bebidas": "🥤"}


def nav_for(user: User | None, path: str) -> list[dict]:
    def allowed(i: NavItem) -> bool:
        return i.access == "public" or (user is not None and (i.access == "staff" or user.is_admin))

    def active(i: NavItem) -> bool:
        return path == "/" if i.href == "/" else path.startswith(i.href)

    return [{"href": i.href, "label": i.label, "icon": i.icon, "active": active(i)} for i in NAV if allowed(i)]


def cat_icon(cat: str) -> str:
    return CATEGORY_ICONS.get(cat.strip().lower(), "🍨")

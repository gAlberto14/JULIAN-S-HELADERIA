"""Patrón Factory + Inyección de Dependencias: aquí se decide QUÉ implementación usar
y se arma el grafo de objetos. El resto del código no sabe si hay Supabase o memoria."""
from dataclasses import dataclass

from majo.config import Settings
from majo.domain.models import Product
from majo.repositories.base import AuthGateway
from majo.services.services import AccountingService, CatalogService, ReportService, SalesService


@dataclass
class Container:
    auth: AuthGateway
    catalog: CatalogService
    sales: SalesService
    accounting: AccountingService
    reports: ReportService


def build_container(settings: Settings) -> Container:
    if settings.use_supabase:
        from majo.repositories.supabase_repo import build_supabase
        products, sales, expenses, auth = build_supabase(settings)
    else:
        from majo.repositories import memory as m
        products = m.MemoryProductRepository([
            Product("Helado de yogurt natural", "Helados", 6000),
            Product("Yogurt combinado con frutas", "Helados", 9000),
            Product("Maxi cono", "Conos", 8500),
            Product("Copa con kiwi y cerezas", "Copas", 11000),
            Product("Topping extra", "Extras", 2000),
        ])
        sales, expenses, auth = m.MemorySaleRepository(), m.MemoryExpenseRepository(), m.MemoryAuthGateway()
    return Container(auth, CatalogService(products), SalesService(products, sales),
                     AccountingService(sales, expenses), ReportService(sales, expenses))

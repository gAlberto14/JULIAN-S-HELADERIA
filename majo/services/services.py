"""Capa de servicios: reglas de negocio. Solo conocen las interfaces del repositorio."""
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from majo.domain.models import PAYMENT_METHODS, Expense, Product, Sale, SaleItem, User
from majo.repositories.base import ExpenseRepository, ProductRepository, SaleRepository


def now_co() -> datetime:
    return datetime.now(ZoneInfo("America/Bogota"))


class CatalogService:
    def __init__(self, products: ProductRepository):
        self._products = products

    def menu(self): return self._products.list(only_active=True)
    def all(self): return self._products.list()
    def get(self, pid): return self._products.get(pid)

    def save(self, name: str, cat: str, price: float, active: bool, product_id: int | None = None) -> Product:
        name = name.strip()
        if not name or price < 0:
            raise ValueError("Escribe un nombre y un precio válido.")
        return self._products.save(Product(name, cat.strip() or "General", price, active, product_id))

    def delete(self, pid): self._products.delete(pid)

    def toggle(self, pid: int) -> Product | None:
        """Oculta o muestra un producto sin borrarlo."""
        p = self._products.get(pid)
        return self._products.save(replace(p, active=not p.active)) if p else None


class SalesService:
    def __init__(self, products: ProductRepository, sales: SaleRepository):
        self._products, self._sales = products, sales

    def register(self, quantities: dict[int, int], pay: str, user: User) -> Sale:
        if pay not in PAYMENT_METHODS:
            raise ValueError("Forma de pago no válida.")
        items = []
        for pid, qty in quantities.items():
            if qty <= 0:
                continue
            p = self._products.get(pid)  # el precio sale de la BD, nunca del formulario
            if not p or not p.active:
                raise ValueError("Un producto ya no está disponible.")
            items.append(SaleItem(p.id, p.name, p.price, qty))
        if not items:
            raise ValueError("Agrega al menos un producto.")
        now = now_co()
        return self._sales.add(Sale(items, pay, user.name, now.date(), now.strftime("%H:%M")))

    def today(self) -> list[Sale]:
        return list(reversed(self._sales.list(since=now_co().date())))


class AccountingService:
    def __init__(self, sales: SaleRepository, expenses: ExpenseRepository):
        self._sales, self._expenses = sales, expenses

    def add_expense(self, concept: str, amount: float, when: date) -> Expense:
        if not concept.strip() or amount <= 0:
            raise ValueError("Completa el concepto y un valor mayor a 0.")
        return self._expenses.add(Expense(concept.strip(), amount, when))

    def delete_expense(self, eid): self._expenses.delete(eid)

    def ledger(self) -> dict:
        sales, exps = self._sales.list(), self._expenses.list()
        rows = [(s.sale_date, f"Venta {s.sale_time} ({s.pay})", s.total, None) for s in sales]
        rows += [(e.exp_date, e.concept, -e.amount, e.id) for e in exps]
        rows.sort(key=lambda r: r[0], reverse=True)
        income, spent = sum(s.total for s in sales), sum(e.amount for e in exps)
        return {"rows": rows[:80], "income": income, "expenses": spent, "balance": income - spent}


class ReportService:
    def __init__(self, sales: SaleRepository, expenses: ExpenseRepository):
        self._sales, self._expenses = sales, expenses

    def summary(self, days: int | None) -> dict:
        since = now_co().date() - timedelta(days=days - 1) if days else None
        sales, exps = self._sales.list(since), self._expenses.list(since)
        income, spent = sum(s.total for s in sales), sum(e.amount for e in exps)
        units, by_pay, by_day = Counter(), defaultdict(float), defaultdict(float)
        for s in sales:
            by_pay[s.pay] += s.total
            by_day[s.sale_date.isoformat()] += s.total
            for i in s.items:
                units[i.name] += i.qty
        return {
            "income": income, "expenses": spent, "profit": income - spent, "tickets": len(sales),
            "avg": income / len(sales) if sales else 0,
            "top": self._bars(units), "by_pay": self._bars(by_pay, True), "by_day": self._bars(by_day, True, True),
        }

    @staticmethod
    def _bars(data, money=False, by_key=False):
        if by_key:  # por día: orden cronológico, últimos 10
            items = sorted(data.items())[-10:]
        else:       # ranking: de mayor a menor, top 8
            items = sorted(data.items(), key=lambda x: -x[1])[:8]
        top = max((v for _, v in items), default=1) or 1
        return [{"label": k, "value": v, "pct": round(v / top * 100), "money": money} for k, v in items]

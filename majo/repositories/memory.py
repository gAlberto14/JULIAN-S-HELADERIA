"""Implementación en memoria: sirve para modo demo y para pruebas sin internet."""
import secrets
from dataclasses import replace
from datetime import date
from itertools import count

from majo.domain.models import Expense, Product, Sale, User
from majo.repositories.base import AuthGateway, ExpenseRepository, ProductRepository, SaleRepository


class MemoryProductRepository(ProductRepository):
    def __init__(self, seed: list[Product] | None = None):
        self._data: dict[int, Product] = {}
        self._ids = count(1)
        for p in seed or []:
            self.save(p)

    def list(self, only_active=False):
        return [p for p in self._data.values() if p.active or not only_active]

    def get(self, product_id):
        return self._data.get(product_id)

    def save(self, product):
        if product.id is None:
            product = replace(product, id=next(self._ids))
        self._data[product.id] = product
        return product

    def delete(self, product_id):
        self._data.pop(product_id, None)


class MemorySaleRepository(SaleRepository):
    def __init__(self):
        self._data: list[Sale] = []
        self._ids = count(1)

    def add(self, sale):
        sale = replace(sale, id=next(self._ids))
        self._data.append(sale)
        return sale

    def list(self, since: date | None = None):
        return [s for s in self._data if since is None or s.sale_date >= since]


class MemoryExpenseRepository(ExpenseRepository):
    def __init__(self):
        self._data: dict[int, Expense] = {}
        self._ids = count(1)

    def add(self, expense):
        expense = replace(expense, id=next(self._ids))
        self._data[expense.id] = expense
        return expense

    def list(self, since: date | None = None):
        return [e for e in self._data.values() if since is None or e.exp_date >= since]

    def delete(self, expense_id):
        self._data.pop(expense_id, None)


class MemoryAuthGateway(AuthGateway):
    _USERS = {
        "admin@majo.co": ("admin123", User("1", "Administrador", "admin")),
        "mesero@majo.co": ("mesero123", User("2", "Mesero", "mesero")),
    }

    def __init__(self):
        self._sessions: dict[str, User] = {}

    def login(self, email, password):
        entry = self._USERS.get(email.strip().lower())
        if not entry or entry[0] != password:
            return None
        token = secrets.token_urlsafe(24)
        self._sessions[token] = entry[1]
        return token

    def user_from_token(self, token):
        return self._sessions.get(token)

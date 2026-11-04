"""Patrón Repository: contratos (interfaces) que los servicios usan.
Los servicios dependen de ESTAS clases abstractas, no de Supabase."""
from abc import ABC, abstractmethod
from datetime import date

from majo.domain.models import Expense, Product, Sale, User


class ProductRepository(ABC):
    @abstractmethod
    def list(self, only_active: bool = False) -> list[Product]: ...
    @abstractmethod
    def get(self, product_id: int) -> Product | None: ...
    @abstractmethod
    def save(self, product: Product) -> Product: ...
    @abstractmethod
    def delete(self, product_id: int) -> None: ...


class SaleRepository(ABC):
    @abstractmethod
    def add(self, sale: Sale) -> Sale: ...
    @abstractmethod
    def list(self, since: date | None = None) -> list[Sale]: ...


class ExpenseRepository(ABC):
    @abstractmethod
    def add(self, expense: Expense) -> Expense: ...
    @abstractmethod
    def list(self, since: date | None = None) -> list[Expense]: ...
    @abstractmethod
    def delete(self, expense_id: int) -> None: ...


class AuthGateway(ABC):
    @abstractmethod
    def login(self, email: str, password: str) -> str | None:
        """Devuelve un token de sesión o None si las credenciales fallan."""
    @abstractmethod
    def user_from_token(self, token: str) -> User | None: ...

"""Capa de dominio: objetos del negocio, sin saber nada de bases de datos ni web."""
from dataclasses import dataclass
from datetime import date

PAYMENT_METHODS = ("Efectivo", "Tarjeta", "Transferencia")


@dataclass
class Product:
    name: str
    cat: str
    price: float
    active: bool = True
    id: int | None = None


@dataclass
class SaleItem:
    product_id: int
    name: str
    price: float
    qty: int


@dataclass
class Sale:
    items: list[SaleItem]
    pay: str
    by_name: str
    sale_date: date
    sale_time: str
    id: int | None = None

    @property
    def total(self) -> float:
        return sum(i.price * i.qty for i in self.items)


@dataclass
class Expense:
    concept: str
    amount: float
    exp_date: date
    id: int | None = None


@dataclass
class User:
    id: str
    name: str
    role: str  # "admin" | "mesero"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

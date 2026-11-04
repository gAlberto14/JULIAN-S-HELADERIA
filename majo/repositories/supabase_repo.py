"""Implementación con Supabase. Usa las tablas de majo-supabase-schema.sql."""
from datetime import date

from supabase import Client, create_client

from majo.config import Settings
from majo.domain.models import Expense, Product, Sale, SaleItem, User
from majo.repositories.base import AuthGateway, ExpenseRepository, ProductRepository, SaleRepository


class SupabaseProductRepository(ProductRepository):
    def __init__(self, db: Client):
        self._t = lambda: db.table("products")

    @staticmethod
    def _to_model(r) -> Product:
        return Product(r["name"], r["cat"], float(r["price"]), r["active"], r["id"])

    def list(self, only_active=False):
        q = self._t().select("*").order("id")
        if only_active:
            q = q.eq("active", True)
        return [self._to_model(r) for r in q.execute().data]

    def get(self, product_id):
        rows = self._t().select("*").eq("id", product_id).execute().data
        return self._to_model(rows[0]) if rows else None

    def save(self, p):
        row = {"name": p.name, "cat": p.cat, "price": p.price, "active": p.active}
        if p.id is None:
            data = self._t().insert(row).execute().data[0]
        else:
            data = self._t().update(row).eq("id", p.id).execute().data[0]
        return self._to_model(data)

    def delete(self, product_id):
        self._t().delete().eq("id", product_id).execute()


class SupabaseSaleRepository(SaleRepository):
    def __init__(self, db: Client):
        self._t = lambda: db.table("sales")

    def add(self, s):
        row = {
            "sale_date": s.sale_date.isoformat(), "sale_time": s.sale_time, "pay": s.pay,
            "by_name": s.by_name, "total": s.total,
            "items": [{"product_id": i.product_id, "name": i.name, "price": i.price, "qty": i.qty} for i in s.items],
        }
        s.id = self._t().insert(row).execute().data[0]["id"]
        return s

    def list(self, since: date | None = None):
        q = self._t().select("*").order("id")
        if since:
            q = q.gte("sale_date", since.isoformat())
        return [
            Sale([SaleItem(**i) for i in r["items"]], r["pay"], r["by_name"] or "",
                 date.fromisoformat(r["sale_date"]), r["sale_time"] or "", r["id"])
            for r in q.execute().data
        ]


class SupabaseExpenseRepository(ExpenseRepository):
    def __init__(self, db: Client):
        self._t = lambda: db.table("expenses")

    def add(self, e):
        row = {"concept": e.concept, "amount": e.amount, "exp_date": e.exp_date.isoformat()}
        e.id = self._t().insert(row).execute().data[0]["id"]
        return e

    def list(self, since: date | None = None):
        q = self._t().select("*").order("id")
        if since:
            q = q.gte("exp_date", since.isoformat())
        return [Expense(r["concept"], float(r["amount"]), date.fromisoformat(r["exp_date"]), r["id"]) for r in q.execute().data]

    def delete(self, expense_id):
        self._t().delete().eq("id", expense_id).execute()


class SupabaseAuthGateway(AuthGateway):
    def __init__(self, auth_client: Client, db: Client):
        self._auth, self._db = auth_client, db

    def login(self, email, password):
        try:
            res = self._auth.auth.sign_in_with_password({"email": email.strip(), "password": password})
            return res.session.access_token
        except Exception:
            return None

    def user_from_token(self, token):
        try:
            u = self._auth.auth.get_user(token).user
            rows = self._db.table("profiles").select("name,role").eq("id", u.id).execute().data
            return User(u.id, rows[0]["name"] or u.email, rows[0]["role"]) if rows else None
        except Exception:
            return None


def build_supabase(s: Settings):
    # Dos clientes: el de datos usa la service key (solo en el servidor, nunca en el navegador)
    # y el de autenticación usa la anon key para no mezclar sesiones.
    db = create_client(s.supabase_url, s.supabase_service_key)
    auth_client = create_client(s.supabase_url, s.supabase_anon_key)
    return (SupabaseProductRepository(db), SupabaseSaleRepository(db),
            SupabaseExpenseRepository(db), SupabaseAuthGateway(auth_client, db))

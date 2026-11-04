"""Configuración leída desde variables de entorno (.env)."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    @property
    def use_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key and self.supabase_service_key)

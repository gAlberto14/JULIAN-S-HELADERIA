# Despliegue en Render o Railway

> **Netlify no ejecuta Python/FastAPI**: sus Functions solo soportan JavaScript/TypeScript.
> Para este proyecto usa Render o Railway (ambos soportan Python de forma nativa).

El proyecto ya incluye:

| Archivo | Para qué sirve |
|---|---|
| `render.yaml` | Blueprint de Render (servicio, build, start, health check y variables). |
| `railway.json` | Configuración de despliegue en Railway (Nixpacks + start + health check). |
| `Procfile` | Comando de arranque para Railway/Heroku y otros PaaS. |
| `.python-version` | Fija Python 3.12.7 en Render y Nixpacks. |
| `.gitignore` | Evita subir `.env`, `.venv` y `__pycache__`. |

La app expone `GET /healthz` para que la plataforma compruebe que está viva.

---

## 0. Sube el código a Git

Render y Railway despliegan desde un repositorio. Si esta carpeta todavía no es un repo:

```bash
git init
git add .
git commit -m "Preparar despliegue en Render/Railway"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/majo-app.git
git push -u origin main
```

`.gitignore` ya excluye `.env`, `.venv` y `__pycache__`.

---

## 1. Prepara Supabase (recomendado)

1. Crea un proyecto en [supabase.com](https://supabase.com).
2. Abre **SQL Editor** y ejecuta el contenido de `majo-supabase-schema.sql`.
3. En **Authentication > Users** crea el usuario administrador y los meseros.
4. Convierte tu usuario en admin (cambia el correo):

   ```sql
   update public.profiles
   set role = 'admin'
   where id = (select id from auth.users where email = 'TU_CORREO');
   ```

5. Copia estos valores de **Project Settings > API**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` (pública)
   - `SUPABASE_SERVICE_KEY` (secreta, solo servidor)

> Si no configuras estas variables, la app arranca en **modo demo** con datos en memoria.
> En un hosting eso significa que las ventas se pierden al reiniciar y que no debes usar
> más de una instancia (cada instancia tendría sus propios datos).

---

## 2. Opción A: Render (recomendada)

### Con Blueprint

1. Sube el proyecto a GitHub/GitLab.
2. En Render: **New > Blueprint** y selecciona el repositorio.
3. Render lee `render.yaml` y pide los valores de `SUPABASE_URL`, `SUPABASE_ANON_KEY` y
   `SUPABASE_SERVICE_KEY`.
4. Pulsa **Apply**. Cuando termine, la URL pública será algo como
   `https://majo-app.onrender.com`.

### Manual (sin Blueprint)

- **New > Web Service** > conecta el repo.
- Runtime: **Python 3**.
- Build command: `pip install -r requirements.txt`
- Start command:
  ```bash
  uvicorn majo.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"
  ```
- Health check path: `/healthz`
- Agrega las variables de entorno de Supabase.

> El plan free de Render duerme el servicio tras un rato sin tráfico; la primera visita
> puede tardar unos segundos en despertar.

---

## 3. Opción B: Railway

1. Sube el proyecto a GitHub.
2. En [railway.app](https://railway.app): **New Project > Deploy from GitHub repo**.
3. Railway detecta Python con Nixpacks y usa `railway.json` / `Procfile`.
4. En **Variables** agrega `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `SUPABASE_SERVICE_KEY`.
5. En **Settings > Networking** pulsa **Generate Domain**.

Railway inyecta `$PORT` automáticamente; no lo definas a mano.

---

## 4. Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `SUPABASE_URL` | No* | URL del proyecto Supabase. |
| `SUPABASE_ANON_KEY` | No* | Anon key (cliente de autenticación). |
| `SUPABASE_SERVICE_KEY` | No* | Service key (solo servidor, nunca en el navegador). |

\* Las tres deben estar presentes para activar Supabase. Si falta alguna, se usa el modo demo.

No subas `.env` al repositorio. En Render/Railway las variables se configuran en el panel.

---

## 5. Comprobar el despliegue

```bash
curl https://TU-DOMINIO/healthz
# {"status":"ok"}
```

Luego abre `/`, `/login` y `/ventas` con un usuario real.

Si usas el modo demo, las credenciales son:

- Admin: `admin@majo.co` / `admin123`
- Mesero: `mesero@majo.co` / `mesero123`

---

## 6. Notas de producción

- **Un solo worker**: con el modo demo (memoria) usa una sola instancia/worker. Con
  Supabase puedes escalar, pero mantén `--workers 1` salvo que midas el consumo.
- **Cookies**: la cookie de sesión se marca `Secure` automáticamente cuando la petición
  llega por HTTPS. Por eso el start command incluye `--proxy-headers` y
  `--forwarded-allow-ips="*"` (Render/Railway están detrás de un proxy).
- **Service key**: nunca la pongas en plantillas, JavaScript ni variables públicas.
- **Migraciones**: el esquema se ejecuta a mano en Supabase; no hay migraciones automáticas.
- **Logs**: revisa los logs del servicio si `/healthz` falla o el build no termina.

---

## 7. Probar el arranque de producción en local

```bash
pip install -r requirements.txt
uvicorn majo.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
# http://127.0.0.1:8000/healthz
```

# Git-Alpha Engine

Full-stack project with **FastAPI backend** and **React + Vite + Tailwind frontend**.

This version includes:

- JWT-based authentication (email + password)
- Modular backend structure (models, schemas, routes, services)
- User profile (name + avatar)
- User preferences (theme, default tab, risk profile)
- Watchlist with optional alert rules (target price, direction)
- AI-powered asset analytics + semantic search (via `ai_engine`)
- WebSocket real-time alerts
- Simple non-Docker setup instructions

---

## 1. Backend (FastAPI)

### 📂 Structure

```bash
backend/
  app/
    __init__.py          # create_app()
    db.py                # SQLAlchemy engine, SessionLocal, Base
    models.py            # User, Watchlist, UserPreference
    schemas.py           # Pydantic models
    core/
      security.py        # hashing, JWT, get_current_user()
    services/
      ai_engine.py       # AlphaEngine (existing AI logic)
    api/
      auth.py            # /api/register, /api/login, /api/me
      profile.py         # /api/profile, /api/profile/avatar
      preferences.py     # /api/preferences
      watchlist.py       # /api/watchlist
      assets.py          # /api/assets, /api/search
      websocket.py       # /ws WebSocket alerts
  main.py                # app entry (uvicorn main:app)
  static/                # user avatars
  requirements.txt
```

### 🔧 Setup (no Docker)

From the `backend` folder:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS / Linux
cd
pip install -r requirements.txt

# Run the API
uvicorn main:app --reload
```

Backend runs at: **http://127.0.0.1:8000**

Environment variables (optional):

- `DATABASE_URL` (default: `sqlite:///./users.db`)
- `SECRET_KEY` (default: `"change-me"`, you SHOULD override)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `60`)

To change them on Windows PowerShell:

```bash
$env:SECRET_KEY = "your-secret-key"
$env:DATABASE_URL = "sqlite:///./users.db"
```

---

## 2. Frontend (React + Vite + Tailwind)

From the `frontend` folder:

```bash
npm install
npm run dev
```

Frontend runs at: **http://127.0.0.1:5173**

Create a `.env` inside `frontend`:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

Make sure the backend is running before using the app.

---

## 3. Auth Flow (JWT)

- `POST /api/register` – create user
- `POST /api/login` – returns `{ access_token }`
- Frontend should store the token (e.g. `localStorage`) and send it as:

```http
Authorization: Bearer <access_token>
```

Protected endpoints:

- `GET /api/me`
- `GET /api/profile`, `PUT /api/profile`, `POST /api/profile/avatar`
- `GET/PUT /api/preferences`
- `GET/POST/DELETE /api/watchlist`

---

## 4. Watchlist & Rules

- `POST /api/watchlist` – body:

```json
{
  "asset_id": "bitcoin",
  "target_price": 50000,
  "direction": "above"
}
```

- If the item for same `asset_id` already exists for this user, its rule is updated.
- Future logic for triggering alerts can read `target_price` + `direction`.

---

## 5. Deployment idea (without Docker)

You can deploy using:

- **Render / Railway**: Use their native Python app template:
  - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Set `DATABASE_URL`, `SECRET_KEY` as environment variables.
- Or a simple **VPS**:
  - Run `uvicorn` behind **Nginx** or **Caddy** as reverse proxy.
  - Use `systemd` service to keep it always running.

---

## 6. Transferring to Another System (e.g., Mac)

Want to move this project to macOS or another computer?

**Quick Start:**
1. See **[TRANSFER_GUIDE.md](TRANSFER_GUIDE.md)** for detailed instructions
2. See **[TRANSFER_CHECKLIST.md](TRANSFER_CHECKLIST.md)** for quick reference

**Automated Setup on Mac:**
```bash
chmod +x setup-mac.sh
./setup-mac.sh
```

**Key Differences (Windows → Mac):**
- Activate venv: `source venv/bin/activate` (not `.\venv\Scripts\activate`)
- Python command: `python3` (not `python`)
- Paths use `/` instead of `\`

**What NOT to transfer:**
- `backend/venv/` (recreate on new system)
- `frontend/node_modules/` (reinstall on new system)
- Optional: `backend/*.db` (unless you want existing data)

---

## 7. Deployment (Production)

If you want, I can also prepare:
- A sample `systemd` service file
- A sample Nginx config for production

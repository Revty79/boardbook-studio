# BoardBook Studio (MVP)

BoardBook Studio is a local-first children's board-book illustration assistant.

This MVP includes:
- Next.js + TypeScript + Tailwind frontend
- FastAPI backend with PostgreSQL
- Local image storage (`backend/media`)
- Mock LLM + mock image generation providers
- Placeholder provider files for future Ollama and ComfyUI integrations

## Architecture

### Backend (`backend/`)
- `app/main.py`: FastAPI app bootstrap, CORS, static media mounting, startup table creation + seed
- `app/models/entities.py`: SQLAlchemy entities
- `app/api/routes/*`: route modules for dashboard, projects, characters, style profiles, story pages, generations
- `app/services/generation_service.py`: prompt build + generate/refine/approve orchestration
- `app/providers/*`: provider interfaces + mock/placeholder implementations
- `app/seed.py`: demo seed data (1 project, 1 character, 1 style profile, 1 story page, 1 generation)

### Frontend (`frontend/`)
- App Router pages for all MVP screens:
  - Dashboard
  - Projects list
  - Project detail
  - Character library
  - Character detail/edit + reference upload
  - Style profile
  - Story pages list
  - Page editor (text input, prompt preview, generate, refine, version history, approve)
- `lib/api.ts`: typed frontend API client

## Local Setup

## 1) Start Postgres

```bash
docker compose up -d postgres
```

## 2) Configure env files

```bash
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env.local
```

If your shell does not support `copy`, use your OS file copy command.

## 3) Start backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 4) Start frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.
Backend runs at `http://localhost:8000`.

## Demo Data

On first backend startup, demo data is seeded automatically if the database is empty:
- 1 project
- 1 character
- 1 style profile
- 1 story page
- 1 mock generation image

## MVP Verification Checklist

1. Open `http://localhost:3000` and confirm dashboard loads counts.
2. Go to Projects and create/edit a project.
3. Open project and create/edit a character.
4. Upload a character reference image on character detail.
5. Edit and save style profile.
6. Create a story page and open its editor.
7. Paste story text and click **Generate Image**.
8. Confirm image appears with a new version in history.
9. Enter refinement text and submit.
10. Confirm a new generation version is created and linked.
11. Click **Approve Selected** and confirm approved marker appears.

## Notes on Providers

Current defaults are mock providers:
- `MockLLMProvider`: returns deterministic structured prompt text
- `MockImageProvider`: creates placeholder PNG output in `backend/media/generated/`

Future integration stubs (not active yet):
- `OllamaProvider`
- `ComfyUIProvider`

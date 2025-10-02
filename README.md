Django REST API for NativeSpeak frontend

This project provides endpoints to replace front-end localStorage usage from the NativeSpeak demo.

Setup (Windows PowerShell):

1. Create a virtualenv and activate it:
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Install dependencies:
   pip install django djangorestframework django-cors-headers

3. Run migrations and start server:
   py  m
   anage.py migrate
   py -3 manage.py runserver

Available endpoints:
- /api/settings/ (GET, POST, PUT)
- /api/tools/ (list, retrieve, create, update, delete)
- /api/logs/ (GET, POST)
- /api/achievements/ (GET, POST)
- /api/notifications/ (list, create)
- /api/presence/ (list, update)
- /api/todos/ (list, create, update, delete)
- /api/lessons/ (list, retrieve)
- /api/ui-state/ (GET, PUT)
 - /api/auth/ (register/login)

Use /api-auth/ for browsable API authentication (optional).

Frontend dev server & API proxy
------------------------------

When developing the frontend (the `NativeSpeak-main` Vite app) you'll want the browser to send `/api` requests to the Django backend (default http://127.0.0.1:8000). There are two common ways to make this work during development:

1) Set the VITE_API_URL environment variable (recommended)

 - This tells the frontend to prefix API requests with the backend URL. In PowerShell you can run the Vite dev server with:

```powershell
# from the NativeSpeak-main directory
$env:VITE_API_URL = 'http://127.0.0.1:8000'
npm run dev
```

Or set it for a single command:

```powershell
$env:VITE_API_URL = 'http://127.0.0.1:8000'; npm run dev
```

2) Configure the Vite dev server proxy (alternate)

 - Edit `NativeSpeak-main/vite.config.ts` and add a proxy so requests to `/api` are forwarded to the backend:

```ts
// vite.config.ts (excerpt)
export default defineConfig({
   server: {
      proxy: {
         '/api': {
            target: 'http://127.0.0.1:8000',
            changeOrigin: true,
            secure: false,
         },
      },
   },
});
```

Notes
 - The frontend stores access and refresh tokens in `localStorage` (keys `auth:access` and `auth:refresh`). Other UI and settings are saved via the backend API when available; if the API is unreachable the frontend falls back to `localStorage` for those items.
 - If you see 404 responses coming from the Vite dev server for `/api` requests, either set `VITE_API_URL` or configure the proxy as above so requests reach Django instead of Vite.


# Analytics testing

Run backend tests:

```bash
cd backend
PYTHONPATH=. pytest -q
```

Run frontend checks:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

Analytics tests cover administrator authorization, empty datasets, date validation, and CSRF-protected CSV export. Test data uses an isolated SQLite database; no paid services are required.

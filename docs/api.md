# API

Public routes are under `/api/v1`:

- `GET /health`
- `GET /languages`
- `GET /categories`
- `GET /courses?search=&language=&level=&category=&page=&page_size=`
- `GET /courses/{slug}`
- `GET /courses/{slug}/modules`
- `GET /lessons/{id}`
- `GET /paths`

Course results are paginated and only published courses, modules, lessons, and paths are exposed.

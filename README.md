# Ride-hailing backend API

A REST API built with **Django 5.0**, **Django REST Framework (DRF)**, **PostgreSQL 16**, and **uv** for the backend engineering assessment.

---

## Table of contents
- [Architecture and tech stack](#architecture-and-tech-stack)
- [Quickstart: local evaluation](#quickstart-local-evaluation)
- [Developer experience and VS Code integration](#developer-experience-and-vs-code-integration)
- [API endpoints and browsable API guide](#api-endpoints-and-browsable-api-guide)
- [Architectural deep dives](#architectural-deep-dives)
  - [1. Strict two-query budget](#1-strict-two-query-budget)
  - [2. Database-level distance sorting](#2-database-level-distance-sorting)
  - [3. Dynamic query parameter reflection and validation](#3-dynamic-query-parameter-reflection-and-validation)
  - [4. Schema precision with a custom user model](#4-schema-precision-with-a-custom-user-model)
  - [5. Automated startup and relative date shifting](#5-automated-startup-and-relative-date-shifting)
- [Bonus SQL report](#bonus-sql-report)

---

## Architecture and tech stack

- **Python 3.12** / **Django 5.0.14** / **Django REST Framework 3.17.2**
- **PostgreSQL 16 (Alpine)**: Relational database with database-level check constraints and indexed foreign keys.
- **Astral `uv`**: Ultra-fast, deterministic Python package resolver and virtual environment manager (`uv.lock`).
- **Docker Compose**: Containerized multi-service setup isolating runtime dependencies and eliminating local environment mismatches.
- **Django Debug Toolbar**: Configured for performance analysis and query count profiling.

---

## Quickstart: local evaluation

Docker Compose runs Django and PostgreSQL without a host Python installation. Create a local environment file from the example before starting:

### 1. Start the stack

```bash
cp .env.example .env
docker compose up -d --build
```

### 2. What happens on startup
The container entrypoint (`scripts/dev_entry`) runs a pipeline:
1. Polls the database socket until PostgreSQL is accepting traffic.
2. Applies all database migrations automatically (`migrate --no-input`).
3. Loads `users` followed by `rides` (102 objects total).
4. Re-timestamps ride events to within the last 24 hours relative to startup time. This guarantees that **Requirement #4**'s 24-hour event filter is immediately demonstrable.
5. Provisions the evaluation administrator account if it does not already exist.

### 3. Access the API
- **Root API URL:** [http://localhost:8000/api/](http://localhost:8000/api/)
- **Default Evaluation Credentials:**
  - **Email:** `admin@test.com`
  - **Password:** `123`
  - **Role:** `admin`
---

## Developer experience and VS Code integration

### Running management commands
You can run any Django command directly through Docker Compose:

```bash
# Run Django system checks
docker compose exec app python manage.py check

# Open a Django shell
docker compose exec app python manage.py shell

# View live container logs
docker compose logs -f app
```

### Container development with VS Code
For reviewers and developers who prefer working directly in an integrated terminal without prefixing commands with `docker compose exec`:

1. Install the **Dev Containers** (or **Docker**) extension in VS Code.
2. Open the Docker tab in the VS Code sidebar.
3. Under **Containers**, right-click `ride-hailing-be-app-1` and select **Attach Visual Studio Code**.
4. Open an integrated terminal to have direct, instant shell access within the environment. Try `python manage.py shell_plus --print-sql`.

---

## API endpoints and browsable API guide

The viewsets listed below use `AdministratorPermission`: requests need an authenticated user with `role='admin'`.

### Endpoints overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | [`/api/rides/`](http://localhost:8000/api/rides/) | Optimized list of rides with 24-hour prefetched events, filtering, sorting, and pagination. |
| `POST` | [`/api/rides/`](http://localhost:8000/api/rides/) | Create a new ride. |
| `GET, PUT, PATCH, DELETE` | `/api/rides/{id}/` | Retrieve, update, or delete a specific ride. |
| `GET` | [`/api/naive/`](http://localhost:8000/api/naive/) | Naive comparison endpoint demonstrating the unoptimized N+1 query problem. |
| `GET, POST` | [`/api/users/`](http://localhost:8000/api/users/) | List or create users. |
| `GET, PUT, PATCH, DELETE` | `/api/users/{id}/` | Retrieve, update, or delete a specific user. |
| `GET, POST` | [`/api/ride-events/`](http://localhost:8000/api/ride-events/) | List or create ride events. |
| `GET, PUT, PATCH, DELETE` | `/api/ride-events/{id}/` | Retrieve, update, or delete a specific ride event. |

---

### Ride list query parameters (`/api/rides/`)

The ride list endpoint supports strict query parameter validation. Undeclared query parameters trigger an immediate `HTTP 400 Bad Request`.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `status` | string | Exact filter on ride status (`ASSIGNED`, `CANCELLED`, `COMPLETED`, `IN_PROGRESS`, `REQUESTED`, `SCHEDULED`). |
| `rider_email` | string | Filter rides by the rider's email address (via foreign key join). |
| `sort_by` | string | Sort field: `pickup_time`, `-pickup_time`, `distance`, `-distance`. |
| `target_lat` | float | Target latitude between `-90.0` and `90.0` (required when `sort_by=distance`). |
| `target_long` | float | Target longitude between `-180.0` and `180.0` (required when `sort_by=distance`). |
| `p` | int | Page number (default: 1). |
| `ps` | int | Page size (default: 10, max: 20). |

#### Example requests

```bash
# Filter completed rides sorted by pickup time
curl -u admin@test.com:123 "http://localhost:8000/api/rides/?status=COMPLETED&sort_by=pickup_time"

# Sort rides by distance from target GPS coordinates
curl -u admin@test.com:123 "http://localhost:8000/api/rides/?sort_by=distance&target_lat=14.5547&target_long=121.0244"

# Filter by rider email with custom page size
curl -u admin@test.com:123 "http://localhost:8000/api/rides/?rider_email=alex.rider@example.com&ps=15"
```

---

## Architectural deep dives

### 1. Strict two-query budget

#### Requirement
The assessment calls for returning rides and their recent events within a two-query data budget (or three with pagination's COUNT query). The serializer exposes rider and driver IDs, not nested user records.

#### Implementation
[`RideViewSet.get_queryset()`](apps/rides/views/ride.py) uses Django ORM's `Prefetch` with `to_attr`:

```python
time_threshold = timezone.now() - timezone.timedelta(hours=24)

return Ride.objects.prefetch_related(
    Prefetch(
        'events',
        queryset=RideEvent.objects.filter(created_at__gte=time_threshold),
        to_attr='todays_ride_events'
    )
)
```

#### Verification with JSON requests
For a paginated JSON list, the ride page and prefetched events take two data queries; pagination adds a COUNT query. Authentication or browsable API rendering can add further queries. The following SQL illustrates the default page:

```sql
SELECT COUNT(*) AS "__count" FROM "rides_ride";

SELECT "rides_ride"."id", "rides_ride"."status", "rides_ride"."id_rider_id",
       "rides_ride"."id_driver_id", "rides_ride"."pickup_latitude",
       "rides_ride"."pickup_longitude", "rides_ride"."dropoff_latitude",
       "rides_ride"."dropoff_longitude", "rides_ride"."pickup_time"
FROM "rides_ride" ORDER BY "rides_ride"."id" ASC LIMIT 10;

SELECT "rides_rideevent"."id", "rides_rideevent"."ride_id",
       "rides_rideevent"."description", "rides_rideevent"."created_at"
FROM "rides_rideevent"
WHERE ("rides_rideevent"."created_at" >= '[24h_timestamp]'
       AND "rides_rideevent"."ride_id" IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10));
```

---

### 2. Database-level distance sorting

When `sort_by=distance` (or `-distance`), the API calculates great-circle distance from the supplied target to each ride's pickup point. At a high level:

```text
require both target coordinates
represent the target coordinates as numeric SQL values
convert the target and pickup coordinates to radians
calculate the latitude and longitude gaps
combine the squared half-angle sines, weighted by the latitudes' cosines
convert the result to a central angle using square root and arcsine
multiply by Earth's radius to get distance in kilometres
annotate rides with the computed distance
sort by distance in SQL (reverse for -distance), then paginate
```

The ORM implementation is in [`apps/rides/filters/rides.py`](apps/rides/filters/rides.py), in `RideOrdering.get_distance_query()` and `RideOrdering.filter_queryset()`. Computing the sort in SQL avoids loading every ride into Python before pagination; a computed distance sort is **not** automatically index-backed.

#### Formula & Algorithmic References

The distance is computed using the **Haversine formula**, which remains numerically well-conditioned for small spherical distances:

$$a = \sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1) \cdot \cos(\text{lat}_2) \cdot \sin^2\left(\frac{\Delta\text{lon}}{2}\right)$$

$$c = 2 \cdot \arcsin\left(\sqrt{a}\right)$$

$$d = R \cdot c \quad (R = 6371.0\text{ km})$$

- **Algorithmic Reference:** Implemented following the formulations documented in [Movable Type Scripts: Calculate distance, bearing and more between Latitude/Longitude points](https://www.movable-type.co.uk/scripts/latlong.html), mapped onto PostgreSQL database functions (`ASin`, `Sqrt`, `Cos`, `Sin`, `Radians`, and `Power`).

---

### 3. Dynamic query parameter reflection and validation

Standard DRF serializers silently drop unexpected query parameters during `to_internal_value()`. To prevent silent API misuse, [`@validate_query_params`](apps/rides/utils/decorators.py) enforces strict validation:

1. Dynamically inspects the view's active `pagination_class` using regex over `dir(paginator)` to extract active query parameters (e.g. `p`, `ps`).
2. Combines declared serializer fields (`sort_by`, `status`, `rider_email`, `target_lat`, `target_long`) with discovered pagination and debug parameters.
3.  If an incoming query parameter falls outside the allowed set, it raises `ValidationError(f"Invalid query params: [...]")`, returning `HTTP 400 Bad Request`.
4. If `sort_by=distance` or `-distance` is passed, field validation requires both valid `target_lat` and `target_long` coordinates.

---

### 4. Schema precision with a custom user model

Rather than subclassing `AbstractUser` (which includes a `username` column), [`User`](apps/users/models/users.py) subclasses **`AbstractBaseUser`** and **`PermissionsMixin`**:

- **Schema:** The user table has `id`, `email`, `role`, `first_name`, `last_name`, `phone_number`, and authentication fields (including passwords and permission flags).
- **Database constraints:**
  - `ph_phone_number_international_format_constraint`: Enforces the Philippine phone format (`^\+639\d{9}$`).
  - `role_constraint`: Enforces valid role choices (`admin`, `driver`, `rider`).
- **Custom `UserManager`:** Implements `create_user` and `create_superuser` with email normalization and automatic administrative role assignment.

---

### 5. Automated startup and relative date shifting

Fixture timestamps are fixed, so events eventually fall outside the "last 24 hours" filter. At startup, [`scripts/update_fixtures.py`](scripts/update_fixtures.py) randomly selects roughly half of the fixture event IDs and gives them a timestamp within the previous 24 hours. The others retain their historical dates, allowing recent and older events to be compared. After a day without a restart, refreshed events may age out of the window.

---

## Bonus SQL report

*(Reserved for a bonus report on trips exceeding one hour, grouped by month and driver.)*

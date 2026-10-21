# Ride-Hailing Backend API

A high-performance RESTful API built with **Django 5.0**, **Django REST Framework (DRF)**, **PostgreSQL 16**, and **uv**, developed for the backend engineering assessment.

---

## Table of Contents
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Quickstart: Zero-Config Evaluation](#quickstart-zero-config-evaluation)
- [Developer Experience & VS Code Integration](#developer-experience--vs-code-integration)
- [API Endpoints & Browsable API Guide](#api-endpoints--browsable-api-guide)
- [Architectural Deep Dives & Performance Engineering](#architectural-deep-dives--performance-engineering)
  - [1. Strict 2-Query Budget & The Browsable API Illusion](#1-strict-2-query-budget--the-browsable-api-illusion)
  - [2. Database-Level Haversine Formula for Distance Sorting](#2-database-level-haversine-formula-for-distance-sorting)
  - [3. Dynamic Query Parameter Reflection & Validation](#3-dynamic-query-parameter-reflection--validation)
  - [4. Schema Precision with Custom User Model](#4-schema-precision-with-custom-user-model)
  - [5. Automated Startup & Relative Date Shifting Pipeline](#5-automated-startup--relative-date-shifting-pipeline)
- [Bonus SQL Report](#bonus-sql-report)

---

## Architecture & Tech Stack

- **Python 3.12** / **Django 5.0.14** / **Django REST Framework 3.15**
- **PostgreSQL 16 (Alpine)**: Relational database with database-level check constraints and indexed foreign keys.
- **Astral `uv`**: Ultra-fast, deterministic Python package resolver and virtual environment manager (`uv.lock`).
- **Docker Compose**: Containerized multi-service setup isolating runtime dependencies and eliminating local environment mismatches.
- **Django Debug Toolbar**: Configured for performance analysis and query count profiling.

---

## Quickstart: Zero-Config Evaluation

To ensure the application can be tested immediately on any machine without installing Python or configuring local databases, the entire stack is containerized with an automated startup and seeding sequence.

### 1. Start the stack
Clone the repository and run:

```bash
docker compose up -d --build
```

### 2. What happens on startup
The container entrypoint (`scripts/dev_entry`) runs pipeline:
1. **Databse Readiness**: Polls the database socket until PostgreSQL is accepting traffic.
2. **Schema Migrations**: Applies all database migrations automatically (`migrate --no-input`).
3. **Sequential Fixture Seeding**: Loads `users` followed by `rides` (102 objects total).
4. **Timestamp Shifting**: Re-timestamps ride events to within the last 24 hours relative to startup time. This guarantees that **Requirement #4**'s 24-hour event filter is immediately demonstrable.
5. **Superuser Creation**: Provisions the evaluation administrator account if it does not already exist.

### 3. Access the API
- **Root API URL:** [http://localhost:8000/api/](http://localhost:8000/api/)
- **Default Evaluation Credentials:**
  - **Email:** `admin@test.com`
  - **Password:** `123`
  - **Role:** `admin`
---

## Developer Experience & VS Code Integration

### Running Management Commands
You can run any Django command directly through Docker Compose:

```bash
# Run Django system checks
docker compose exec app python manage.py check

# Open a Django shell
docker compose exec app python manage.py shell

# View live container logs
docker compose logs -f app
```

### Immersive Container Development via VS Code
For reviewers and developers who prefer working directly in an integrated terminal without prefixing commands with `docker compose exec`:

1. Install the **Dev Containers** (or **Docker**) extension in VS Code.
2. Open the Docker tab in the VS Code sidebar.
3. Under **Containers**, right-click `ride-hailing-be-app-1` and select **Attach Visual Studio Code**.
4. Open an integrated terminal to have direct, instant shell access within the environment. Try `python manage.py shell_plus --print-sql`.

---

## API Endpoints & Browsable API Guide

All endpoints are strictly protected by `AdministratorPermission`, enforcing that only authenticated users with `role='admin'` can perform operations.

### Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/rides/` | Optimized list of rides with 24-hr prefetched events, filtering, sorting, and pagination. |
| `POST` | `/api/rides/` | Create a new ride. |
| `GET, PUT, PATCH, DELETE` | `/api/rides/{id}/` | Retrieve, update, or delete a specific ride. |
| `GET` | `/api/rides/naive/` | Naive comparison endpoint demonstrating the unoptimized N+1 query problem. |
| `GET, POST` | `/api/users/` | List or create users. |
| `GET, PUT, PATCH, DELETE` | `/api/users/{id}/` | Retrieve, update, or delete a specific user. |
| `GET, POST` | `/api/ride-events/` | List or create ride events. |
| `GET, PUT, PATCH, DELETE` | `/api/ride-events/{id}/` | Retrieve, update, or delete a specific ride event. |

---

### Ride List Query Parameters (`/api/rides/`)

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

#### Example Requests
```bash
# Filter completed rides sorted by pickup time
curl -u admin@test.com:123 "http://localhost:8000/api/rides/?status=COMPLETED&sort_by=pickup_time"

# Sort rides by distance from target GPS coordinates
curl -u admin@test.com:123 "http://localhost:8000/api/rides/?sort_by=distance&target_lat=14.5547&target_long=121.0244"

# Filter by rider email with custom page size
curl -u admin@test.com:123 "http://localhost:8000/api/rides/?rider_email=alex.rider@example.com&ps=15"
```

---

## Architectural Deep Dives

### 1. Strict 2-Query Budget & The Browsable API Illusion

#### Requirement
The assessment mandates returning rides with related driver, rider, and last 24-hour events within a **2-query budget** (or 3 including the pagination COUNT query).

#### Implementation
In `RideViewSet.get_queryset()`, queries are optimized using Django ORM's `Prefetch` object with `to_attr`:

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

#### Verification on JSON Requests
When consumed by frontend clients, mobile apps, or `curl` (`Accept: application/json` or `?format=json`), the endpoint executes **strictly 3 queries** (2 queries for data):

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

#### The "Browsable API Form Illusion" (Django Debug Toolbar Note)
When viewing `/api/rides/` in a web browser, Django Debug Toolbar displays **5 queries**. 

**Why this happens:**
- Because `RideViewSet` is a `ModelViewSet`, DRF's `BrowsableAPIRenderer` automatically generates an interactive HTML `<form>` at the bottom of the page to permit `POST` creation.
- `id_rider` and `id_driver` are `ForeignKey` relations. To populate the HTML `<select>` dropdown menus in the browser, DRF executes two choice queries: `SELECT ... FROM users_user LIMIT 1000`.
- **Zero user queries occur during JSON API consumption.** Appending `?format=json` confirms strictly 3 queries.

---

### 2. Database-Level Haversine Formula for Distance Sorting
`RideOrdering` (`apps/rides/filters/rides.py`) executes the **Haversine formula directly inside PostgreSQL** using Django database functions (`ASin`, `Sqrt`, `Cos`, `Sin`, `Radians`, and `Power`):

$$\Delta\sigma = 2 \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1)\cos(\text{lat}_2)\sin^2\left(\frac{\Delta\text{lon}}{2}\right)} \right)$$

$$\text{distance} = 2 R \cdot \arcsin\left(\sqrt{\dots}\right)$$

```python
haversine_a = (
    Power(Sin(deltax / 2), 2) + 
    Cos(target_lat_rad) * Cos(pickup_lat_rad) * Power(Sin(delaty / 2), 2)
)
return 2 * earth_radius_km * ASin(Sqrt(haversine_a))
```

PostgreSQL annotates the computed `distance` column in SQL and uses index-friendly `ORDER BY 10 ASC` (or `DESC` for `-distance`), preserving database-level pagination (`LIMIT 10 OFFSET 0`).

---

### 3. Dynamic Query Parameter Reflection & Validation

Standard DRF serializers silently drop unexpected query parameters during `to_internal_value()`. To prevent silent API misuse, a custom decorator `@validate_query_params` (`apps/rides/utils/decorators.py`) enforces strict validation:

1. **Paginator Reflection:** Dynamically inspects the view's active `pagination_class` using regex over `dir(paginator)` to extract active query parameters (e.g. `p`, `ps`).
2. **Schema Whitelist:** Combines declared serializer fields (`sort_by`, `status`, `rider_email`, `target_lat`, `target_long`) with discovered pagination and debug parameters.
3. **Difference Rejection:** If any incoming query parameter falls outside the allowed set, it raises `ValidationError(f"Invalid query params: [...]")`, returning `HTTP 400 Bad Request`.
4. **Conditional Requirements:** If `sort_by=distance` is passed, field validation verifies that both `target_lat` and `target_long` are present and valid coordinates.

---

### 4. Schema Precision with Custom User Model

Rather than subclassing `AbstractUser` (which forces a legacy `username` column into the database with a uniqueness constraint), `User` subclasses **`AbstractBaseUser`** and **`PermissionsMixin`**:

- **Exact Assessment Schema:** Database table contains solely `id`, `email`, `role`, `first_name`, `last_name`, `phone_number`, and standard auth timestamps/flags.
- **Database Constraints:** 
  - `ph_phone_number_international_format_constraint`: Enforces E.164 Philippine format (`^\+639\d{9}$`).
  - `role_constraint`: Enforces valid role choices (`admin`, `driver`, `rider`).
- **Custom `UserManager`:** Implements `create_user` and `create_superuser` with email normalization and automatic administrative role assignment.

---

### 5. Automated Startup & Relative Date Shifting Pipeline

Because JSON fixtures store static historical dates, fixtures loaded into a database will inevitably fall outside a dynamic "last 24 hours" threshold over time.

To solve this, `scripts/update_fixtures.py` is invoked during container startup:
- Analyzes loaded `RideEvent` records.
- Stochastically adjusts event timestamps relative to `timezone.now()`.
- Guarantees that evaluators booting the project immediately see populated `todays_ride_events` arrays without manual database intervention.

---

## Bonus SQL Report

*(Reserved for Bonus Task: Trips exceeding 1 hour duration grouped by Month and Driver).*

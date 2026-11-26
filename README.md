# Drone API

A REST API for managing drone fleets, missions, and scheduling — built with FastAPI and MongoDB.

The system allows you to register drones, define missions with trajectories, schedule drones to perform those missions, and automatically dispatch them when their start time arrives. An asynchronous background scheduler runs every 2 minutes to start due missions and complete finished ones.

![Collections Schema](image.png)

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) (ASGI) |
| Database | [MongoDB](https://www.mongodb.com/) via [Motor](https://motor.readthedocs.io/) |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) |
| Notifications | [notify-py](https://github.com/ms7m/notify-py) |
| Config | `python-dotenv` |

## Project Structure

```
drone-api/
├── server/
│   ├── main.py               # App entrypoint, background scheduler
│   ├── database.py           # MongoDB connection & collections
│   ├── models.py             # Pydantic request/response models
│   ├── utils.py              # Shared validation helpers
│   ├── mission_scheduler.py  # Background task: fires due missions
│   ├── notifications.py      # Desktop notification sender
│   └── routers/
│       ├── drones.py         # /drones endpoints
│       ├── missions.py       # /missions endpoints
│       └── schedules.py      # /schedules endpoints
└── Drones API.postman_collection.json
```

## Prerequisites

- Docker Desktop with Docker Compose (recommended), or Python 3.9+ and a running MongoDB instance

## Run with Docker

From the project root:

```bash
docker compose up --build
```

This starts the API and MongoDB. MongoDB data is kept in the `mongo-data` Docker volume across restarts. The API is available at `http://localhost:8000`, and Swagger UI is at `http://localhost:8000/docs`.

Stop the containers with `Ctrl+C`, or run `docker compose down`. To also delete the database volume and all stored data, run `docker compose down --volumes`.

### macOS desktop notifications

Containers do not have access to the macOS desktop notification center, so the API container cannot display desktop notifications on the Mac. To test notifications, run MongoDB in Docker and run the API natively on macOS instead:

```bash
docker compose up -d mongo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
DB_URI=mongodb://127.0.0.1:27017 DB_NAME=drone_db \
  .venv/bin/uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
```

## Run natively

To run without Docker, install dependencies with `pip install -r requirements.txt`, set `DB_URI` and `DB_NAME` in a `.env` file or the shell environment, and run:

```bash
uvicorn server.main:app --reload
```

The API will be available at `http://localhost:8000`; interactive docs are at `http://localhost:8000/docs`.

## API Overview

### Drones — `/drones`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/drones/` | List all drones |
| `GET` | `/drones/status/{status}` | Filter drones by status (`available`, `pending`, `on-mission`) |
| `GET` | `/drones/{id}` | Get a drone by ID |
| `POST` | `/drones/` | Register a new drone |
| `PUT` | `/drones/{id}` | Update a drone's status |
| `PUT` | `/drones/{id}/possible_missions` | Update the missions a drone is eligible for |

### Missions — `/missions`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/missions/` | List all missions |
| `POST` | `/missions/` | Create a new mission |

### Schedules — `/schedules`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/schedules/` | List all schedules |
| `GET` | `/schedules/{drone_id}` | Get schedules for a specific drone |
| `GET` | `/schedules/{start_date}/{end_date}` | Get schedules within a date range |
| `POST` | `/schedules/` | Schedule a drone for a mission |
| `PUT` | `/schedules/{id}` | Update a schedule's status |

## Background Scheduler

On startup, an asynchronous background task polls the database every **2 minutes**. For any schedule whose `start_time` has passed and whose status is `pending` or `scheduled`, it:

1. Marks the schedule as `in-progress` and the drone as `on-mission`, recording its `current_mission_id`.
2. Sends a desktop notification via `notify-py`.

When an in-progress schedule's `end_time` has passed, the scheduler marks it `completed` and resets the drone to `available`.

### Testing desktop notifications

Test a notification independently of MongoDB and the API:

```bash
python -c "from server.notifications import send_notification; send_notification(9001)"
```

On macOS, `notify-py` uses its bundled Notificator app and does not support custom notification icons. If no notification appears, allow notifications for Notificator in **System Settings → Notifications**, and ensure the API is running in a logged-in desktop session (not over SSH or in a headless process). Notification send failures are logged and do not stop the mission scheduler.

## Testing

A Postman collection is included at `Drones API.postman_collection.json`. Import it into Postman to explore and test all available endpoints.

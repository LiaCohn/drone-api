# Drone API

A REST API for managing drone fleets, missions, and scheduling — built with FastAPI and MongoDB.

The system allows you to register drones, define missions with trajectories, schedule drones to perform those missions, and automatically dispatch them when their start time arrives. A background scheduler runs every 2 minutes to detect upcoming missions, mark the relevant drone as `on-mission`, and fire a desktop notification.

![Collections Schema](image.png)

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) (ASGI) |
| Database | [MongoDB](https://www.mongodb.com/) via [PyMongo](https://pymongo.readthedocs.io/) |
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

- Python 3.9+
- A running MongoDB instance (local or Atlas)

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd drone-api
   ```

2. **Install dependencies**

   ```bash
   pip install fastapi uvicorn pymongo python-dotenv pydantic notify-py
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   DB_URI=mongodb://localhost:27017
   DB_NAME=drone_db
   ```

4. **Run the server**

   ```bash
   uvicorn server.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.  
   Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

## API Overview

### Drones — `/drones`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/drones/` | List all drones |
| `GET` | `/drones/{status}` | Filter drones by status (`available`, `pending`, `on-mission`) |
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

On startup, a background task polls the database every **2 minutes**. For any schedule whose `start_time` has passed and whose status is `pending` or `scheduled`, it:

1. Marks the drone's status as `on-mission` in MongoDB.
2. Sends a desktop notification via `notify-py`.

## Testing

A Postman collection is included at `Drones API.postman_collection.json`. Import it into Postman to explore and test all available endpoints.

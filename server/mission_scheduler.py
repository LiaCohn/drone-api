from datetime import datetime
import asyncio
import logging

from .database import schedules_collection, drones_collection
from .notifications import send_notification

logger = logging.getLogger(__name__)


async def check_and_fire_missions():
    current_time = datetime.now()

    # Update completed schedules and free up drones
    completed_schedules = await schedules_collection.find(
        {"end_time": {"$lte": current_time}, "status": "in-progress"}
    ).to_list(length=None)
    # Update the status of completed schedules and free up drones
    for schedule in completed_schedules:
        result = await schedules_collection.update_one(
            {
                "id": schedule["id"],
                "end_time": {"$lte": current_time},
                "status": "in-progress",
            },
            {"$set": {"status": "completed"}},
        )
        if result.modified_count != 1:
            continue

        await drones_collection.update_one(
            {"id": schedule["drone_id"]},
            {"$set": {"status": "available", "current_mission_id": None}},
        )
    # Check for missions that need to be fired
    missions_to_fire = await schedules_collection.find(
        {
            "start_time": {"$lte": current_time},
            "status": {"$in": ["pending", "scheduled"]},
        }
    ).to_list(length=None)
    # Fire the missions and update their status to "in-progress"
    for mission in missions_to_fire:
        drone_id = mission["drone_id"]
        try:
            await mark_drone_as_on_mission(drone_id, mission["mission_id"])
        except DroneNotFoundError as error:
            logger.warning("Drone not found: %s", error)
            continue
        except OverlappingError:
            logger.warning("Overlapping mission found for drone %s", drone_id)
            continue
        except UpdateFailedError as error:
            logger.error("Failed to update mission state: %s", error)
            continue
        # Update the schedule status to "in-progress"
        result = await schedules_collection.update_one(
            {
                "id": mission["id"],
                "status": {"$in": ["pending", "scheduled"]},
            },
            {"$set": {"status": "in-progress"}},
        )
        # Check if the update was successful
        if result.modified_count != 1:
            raise UpdateFailedError(
                f"Failed to mark schedule {mission['id']} as in-progress"
            )
        # Send notification to the drone about the mission start
        try:
            await asyncio.to_thread(send_notification, drone_id)
        except Exception:
            logger.exception("Could not send notification for drone %s", drone_id)


class DroneNotFoundError(Exception):
    pass


class UpdateFailedError(Exception):
    pass


class OverlappingError(Exception):
    pass

#function to mark a drone as on-mission
async def mark_drone_as_on_mission(drone_id: int, mission_id: int):
    drone = await drones_collection.find_one(
        {"id": drone_id, "status": {"$ne": "on-mission"}}
    )
    if not drone:
        existing_drone = await drones_collection.find_one({"id": drone_id})
        if existing_drone is None:
            raise DroneNotFoundError(f"Drone with id {drone_id} does not exist")
        raise OverlappingError(f"Drone with id {drone_id} is already on a mission")

    result = await drones_collection.update_one(
        {"id": drone_id, "status": {"$ne": "on-mission"}},
        {
            "$set": {
                "status": "on-mission",
                "current_mission_id": mission_id,
            }
        },
    )
    if result.modified_count != 1:
        raise UpdateFailedError(f"Failed to update drone status with id {drone_id}")

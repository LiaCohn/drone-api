# Create desktop notifications
import platform
from pathlib import Path

from notifypy import Notify


# TODO: change to sms or email
def send_notification(drone_id: int):
    notification = Notify(
        default_notification_application_name="Drone API",
        enable_logging=True,
    )
    notification.title = "Upcoming Schedule"
    notification.message = f"Drone {drone_id} is starting its mission"
    if platform.system() != "Darwin":
        notification.icon = str(Path(__file__).with_name("drone.png"))

    if not notification.send():
        raise RuntimeError(f"Could not send desktop notification for drone {drone_id}")

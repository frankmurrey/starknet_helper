from datetime import datetime, timedelta
from typing import Union


def task_exec_sleep_message(
        time_to_sleep: Union[int, float],
) -> str:
    continue_datetime = datetime.now() + timedelta(seconds=time_to_sleep)
    return (
        f"Time to sleep for {int(time_to_sleep)} seconds..."
        f" Continue at {continue_datetime.strftime('%H:%M:%S')}"
    )

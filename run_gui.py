from src.tasks_executor import TasksExecutor
from gui.main_window.main import run_gui


def on_startup():
    pass
#     Templates().create_not_found_temp_files()
    #
    # if not mingw_installed():
    #     logger.critical("MinGW in not installed.")  # TODO: More info
    #     exit(1)


if __name__ == '__main__':
    task_executor = TasksExecutor()

    on_startup()

    try:
        run_gui()
    except KeyboardInterrupt:
        task_executor.stop()

from gui.main_window.main import run_gui


def on_startup():
    run_gui()
#     Templates().create_not_found_temp_files()
    #
    # if not mingw_installed():
    #     logger.critical("MinGW in not installed.")  # TODO: More info
    #     exit(1)



if __name__ == '__main__':
    on_startup()

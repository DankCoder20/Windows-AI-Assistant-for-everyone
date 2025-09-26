from gui.main_window import MainWindow, create_app


def main() -> None:
    app = create_app()
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()



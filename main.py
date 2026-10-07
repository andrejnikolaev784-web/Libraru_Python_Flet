import flet as ft

from ui.app import LibraryApp

def main(page: ft.Page) -> None:
    LibraryApp(page).run()

if __name__ == "__main__":
    ft.run(main)
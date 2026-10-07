from datetime import datetime

import flet as ft

from report import SessionReport
from services import LibraryService
from ui.pages import CatalogPage, LoansPage, ReadersPage
from ui.theme import AppTheme
from ui.widgets import AlignedTextField, PrimaryButton, StatusBanner

class LibraryApp:
    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._library = LibraryService()
        self._login = AlignedTextField("Логин (UserName)")
        self._banner = StatusBanner("Войдите, чтобы открыть библиотеку")
        self._report: SessionReport | None = None
        self._setup_page()

    def _setup_page(self) -> None:
        self._page.title = "Библиотека · ООП + Flet"
        self._page.padding = 16
        self._page.bgcolor = ft.Colors.WHITE
        self._page.theme_mode = ft.ThemeMode.LIGHT
        try:
            self._page.window.width = 1100
            self._page.window.height = 750
            self._page.window.min_width = 800
            self._page.window.min_height = 600
        except Exception:
            pass
        self._page.on_disconnect = self._on_disconnect

    def _replace(self, control: ft.Control) -> None:
        try:
            self._page.clean()
        except Exception:
            self._page.controls.clear()
        self._page.add(control)
        self._page.update()

    def _on_disconnect(self, e) -> None:
        self._save_report()

    def _save_report(self) -> None:
        if self._report is None:
            return
        self._report.close()
        self._report = None

    def _enter(self, _e=None) -> None:
        name = (self._login.value or "").strip()
        if not name:
            AppTheme.snack_err(self._page, "Введите логин")
            return
        self._report = SessionReport(name, datetime.now())
        self._show_main()

    def _show_login(self) -> None:
        self._replace(
            ft.Container(
                padding=24,
                content=ft.Column(
                    tight=True,
                    spacing=16,
                    controls=[
                        ft.Text("Вход в сессию", size=26, weight=ft.FontWeight.BOLD),
                        self._banner,
                        ft.Row(
                            tight=True,
                            spacing=12,
                            controls=[
                                self._login,
                                PrimaryButton("Войти", on_click=self._enter),
                            ],
                        ),
                        ft.Icon(ft.Icons.LOCAL_LIBRARY, size=40),
                    ],
                ),
            )
        )
        self._page.update()

    def _show_main(self) -> None:
        self._views = [
            LoansPage(self._page, self._library).build(),
            CatalogPage(self._page, self._library).build(),
            ReadersPage(self._page, self._library).build(),
        ]
        self._body = ft.ListView(
            controls=[self._views[0]],
            expand=True,
            spacing=8,
            padding=12,
            auto_scroll=False,
        )
        self._nav = ft.CupertinoNavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.ASSIGNMENT, label="Выдачи"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Каталог"),
                ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label="Читатели"),
            ],
            on_change=self._on_nav,
        )
        try:
            nav = self._nav
        except Exception:
            nav = ft.NavigationBar(
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.ASSIGNMENT, label="Выдачи"),
                    ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Каталог"),
                    ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label="Читатели"),
                ],
                on_change=self._on_nav,
            )
            self._nav = nav

        self._replace(
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    ft.Container(content=self._body, expand=True),
                    self._nav,
                ],
            )
        )

    def _on_nav(self, e) -> None:
        idx = int(getattr(e.control, "selected_index", 0) or 0)
        self._body.controls.clear()
        self._body.controls.append(self._views[idx])
        self._page.update()
    def run(self) -> None:
        self._show_login()
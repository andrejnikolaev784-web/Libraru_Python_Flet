from abc import ABC, abstractmethod

import flet as ft

from services import LibraryService
from ui.theme import AppTheme
from ui.widgets import AlignedTextField, PrimaryButton, StatusBanner

class PageView(ABC):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        self._page = page
        self._library = library

    @abstractmethod
    def build(self) -> ft.Control:
        ...

    def refresh(self) -> None:
        self._page.update()

class CatalogPage(PageView):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        super().__init__(page, library)
        self._list = ft.Column(spacing=6, expand=True, scroll=ft.ScrollMode.AUTO)
        self._title = AlignedTextField("Название")
        self._author = AlignedTextField("Автор")
        self._year = AlignedTextField("Год", width=100, expand=False)
        self._issue = AlignedTextField("№ журнала", width=120, expand=False)
        self._kind = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="book", label="Книга"),
                    ft.Radio(value="mag", label="Журнал"),
                ]
            ),
            value="book",
        )
        self._banner = StatusBanner("Каталог отсортирован через __lt__")

    def _reload(self) -> None:
        self._list.controls.clear()
        for item in self._library.catalog():
            self._list.controls.append(
                ft.ListTile(
                    title=ft.Text(str(item)),
                    subtitle=ft.Text(repr(item)),
                    leading=ft.Icon(
                        ft.Icons.MENU_BOOK if item.available else ft.Icons.LOCK
                    ),
                    trailing=ft.Checkbox(value=item.available, disabled=True),
                )
            )

    def _add(self, _e) -> None:
        try:
            if self._kind.value == "mag":
                self._library.add_magazine(
                    self._title.value or "", int(self._issue.value or "0")
                )
            else:
                self._library.add_book(
                    self._title.value or "",
                    self._author.value or "",
                    int(self._year.value or "0"),
                )
            self._title.value = self._author.value = self._year.value = self._issue.value = ""
            self._reload()
            AppTheme.snack_ok(self._page, "Добавлено")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def build(self) -> ft.Control:
        self._reload()
        return ft.Column(
            [
                ft.Text("Каталог", style=ft.TextThemeStyle.HEADLINE_SMALL),
                self._banner,
                self._kind,
                ft.Row(
                    [self._title, self._author, self._year, self._issue],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [PrimaryButton("Добавить", on_click=self._add)],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Divider(),
                self._list,
            ],
            spacing=AppTheme.GAP,
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

class ReadersPage(PageView):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        super().__init__(page, library)
        self._list = ft.Column(spacing=6, expand=True, scroll=ft.ScrollMode.AUTO)
        self._name = AlignedTextField("ФИО")
        self._ticket = AlignedTextField("Билет", width=160, expand=False)
        self._switch = ft.Switch(label="Только активные читатели", value=True)

    def _reload(self) -> None:
        self._list.controls.clear()
        for r in self._library.readers():
            self._list.controls.append(
                ft.ListTile(title=ft.Text(str(r)), subtitle=ft.Text(repr(r)))
            )

    def _add(self, _e) -> None:
        try:
            self._library.add_reader(self._name.value or "", self._ticket.value or "")
            self._name.value = self._ticket.value = ""
            self._reload()
            AppTheme.snack_ok(self._page, "Читатель зарегистрирован")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def build(self) -> ft.Control:
        self._reload()
        return ft.Column(
            [
                ft.Text("Читатели (≥ 5 объектов)", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row(
                    [
                        self._name,
                        self._ticket,
                        PrimaryButton("Добавить", on_click=self._add),
                        self._switch,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(),
                self._list,
            ],
            spacing=AppTheme.GAP,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

class LoansPage(PageView):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        super().__init__(page, library)
        self._list = ft.Column(spacing=6, expand=True, scroll=ft.ScrollMode.AUTO)
        self._item_dd = ft.Dropdown(label="Издание", expand=True)
        self._reader_dd = ft.Dropdown(label="Читатель", expand=True)
        self._days = ft.Slider(
            min=7, max=30, divisions=23, value=float(LibraryService.loan_days()),
            label="{value} дн.",
        )
        self._progress = ft.ProgressBar(value=0)

    def _fill_dropdowns(self) -> None:
        self._item_dd.options = [
            ft.DropdownOption(key=item.id, text=str(item))
            for item in self._library.catalog()
            if item.available
        ]
        self._reader_dd.options = [
            ft.DropdownOption(key=r.id, text=str(r))
            for r in self._library.readers()
        ]
        total = max(len(self._library.catalog()), 1)
        busy = sum(1 for i in self._library.catalog() if not i.available)
        self._progress.value = busy / total

    def _reload_loans(self) -> None:
        self._list.controls.clear()
        for loan in self._library.loans():
            btn = ft.TextButton(
                "Вернуть",
                disabled=loan.returned,
                on_click=lambda e, lid=loan.id: self._return(lid),
            )
            self._list.controls.append(
                ft.ListTile(title=ft.Text(str(loan)), trailing=btn)
            )

    def _issue(self, _e) -> None:
        try:
            if not self._item_dd.value or not self._reader_dd.value:
                raise ValueError("Выберите издание и читателя")
            self._library.issue(self._item_dd.value, self._reader_dd.value)
            self._item_dd.value = None
            self._fill_dropdowns()
            self._reload_loans()
            AppTheme.snack_ok(self._page, "Выдано")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def _return(self, loan_id: str) -> None:
        try:
            self._library.return_item(loan_id)
            self._fill_dropdowns()
            self._reload_loans()
            AppTheme.snack_ok(self._page, "Возвращено")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def build(self) -> ft.Control:
        self._fill_dropdowns()
        self._reload_loans()
        return ft.Column(
            [
                ft.Text("Выдачи", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row(
                    [
                        self._item_dd,
                        self._reader_dd,
                        PrimaryButton("Выдать", on_click=self._issue),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text("Срок (индикатор)"),
                self._days,
                self._progress,
                ft.Divider(),
                self._list,
            ],
            spacing=AppTheme.GAP,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
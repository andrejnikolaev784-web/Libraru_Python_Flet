import flet as ft

class AlignedTextField(ft.TextField):
    def __init__(self, label: str, **kwargs) -> None:
        kwargs.setdefault("width", 320)
        kwargs.setdefault("expand", False)
        super().__init__(label=label, text_align=ft.TextAlign.LEFT, **kwargs)

class PrimaryButton(ft.FilledButton):
    def __init__(self, caption: str, on_click=None, **kwargs) -> None:
        super().__init__(content=ft.Text(caption), on_click=on_click, **kwargs)

class StatusBanner(ft.Container):
    def __init__(self, text: str = "") -> None:
        self._label = ft.Text(text)
        super().__init__(content=self._label, padding=10, bgcolor=ft.Colors.BLUE_50, border_radius=8)

    def set_text(self, text: str) -> None:
        self._label.value = text
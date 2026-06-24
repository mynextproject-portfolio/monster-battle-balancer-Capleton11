import flet as ft
from i18n import t
from ui_constants import (
    SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_LG, BUTTON_WIDTH_LG,
    TEXT_SIZE_LG, TEXT_SIZE_XL
)


def home_screen(page: ft.Page, on_start):
    """Render the home screen.

    Args:
        page: The Flet page object
        on_start: Callback function to navigate to monster selection
    """
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(height=SPACING_XL * 2),  # Spacer
                ft.Icon(
                    name=ft.Icons.CASTLE,
                    size=120,
                    color=ft.Colors.RED_400,
                ),
                ft.Container(height=SPACING_LG),
                ft.Text(
                    t("home_title"),
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=SPACING_SM),
                ft.Text(
                    t("home_subtitle"),
                    size=TEXT_SIZE_LG,
                    color=ft.Colors.RED_300,
                    text_align=ft.TextAlign.CENTER,
                    italic=True,
                ),
                ft.Container(height=SPACING_XL),
                ft.Container(
                    content=ft.Text(
                        t("home_description"),
                        size=TEXT_SIZE_XL,
                        color=ft.Colors.GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=600,
                ),
                ft.Container(height=SPACING_XL * 2),
                ft.ElevatedButton(
                    t("home_start_button"),
                    width=BUTTON_WIDTH_LG,
                    height=BUTTON_HEIGHT_LG,
                    on_click=on_start,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
    )


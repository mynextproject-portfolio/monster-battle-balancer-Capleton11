import flet as ft
from dnd_api import get_monsters
from i18n import t
from ui_constants import (
    SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_MD, BUTTON_HEIGHT_LG, BUTTON_WIDTH_MD, BUTTON_WIDTH_LG,
    TEXT_SIZE_LG, TEXT_SIZE_XL
)


def monster_selection_screen(page: ft.Page, on_back, on_view_cards):
    """Render the monster selection screen.

    Args:
        page: The Flet page object
        on_back: Callback function to go back to home
        on_view_cards: Callback function to proceed to the cards screen with selected monsters
    """
    # Fetch monsters from API
    monsters = get_monsters()
    
    if not monsters:
        # Show error if monsters failed to load
        return ft.Column(
            [
                ft.Container(height=SPACING_XL),
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                ft.Container(height=SPACING_LG),
                ft.Text(t("monsters_load_error"), size=TEXT_SIZE_XL, color=ft.Colors.RED_400),
                ft.Text(t("connection_error"), size=TEXT_SIZE_LG, color=ft.Colors.GREY_400),
                ft.Container(height=SPACING_XL),
                ft.ElevatedButton(
                    t("back_button"),
                    on_click=on_back,
                    width=BUTTON_WIDTH_MD,
                    height=BUTTON_HEIGHT_MD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    
    # Create dropdown options
    monster_options = [
        ft.dropdown.Option(monster["index"], monster["name"]) 
        for monster in monsters
    ]
    
    # Create dropdowns for monster selection with search enabled
    monster1_dropdown = ft.Dropdown(
        label=t("select_monster_1"),
        options=monster_options,
        width=400,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.AMBER_400,
        text_size=TEXT_SIZE_LG,
        autofocus=False,
    )
    
    monster2_dropdown = ft.Dropdown(
        label=t("select_monster_2"),
        options=monster_options,
        width=400,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_400,
        text_size=TEXT_SIZE_LG,
        autofocus=False,
    )
    
    def handle_view_cards(e):
        """Handle the view cards button click."""
        if monster1_dropdown.value and monster2_dropdown.value:
            on_view_cards(monster1_dropdown.value, monster2_dropdown.value)
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text(t("select_two_warning"))
            )
            page.snack_bar.open = True
            page.update()
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(height=SPACING_LG),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=on_back,
                            tooltip=t("selection_back_tooltip"),
                        ),
                        ft.Text(
                            t("selection_title"),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(height=SPACING_XL),
                ft.Text(
                    t("selection_instruction"),
                    size=TEXT_SIZE_XL,
                    color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=SPACING_XL),
                # Side-by-side monster selection for desktop
                ft.Row(
                    [
                        # Monster 1 selector
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.PERSON, size=30, color=ft.Colors.AMBER_400),
                                            ft.Text(
                                                t("monster_1"),
                                                size=TEXT_SIZE_XL,
                                                color=ft.Colors.AMBER_400,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10,
                                    ),
                                    ft.Container(height=SPACING_SM),
                                    monster1_dropdown,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=SPACING_LG,
                            border=ft.border.all(2, ft.Colors.AMBER_400),
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_800,
                        ),
                        # VS indicator
                        ft.Container(
                            content=ft.Text(
                                "VS",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED_400,
                            ),
                            width=80,
                            alignment=ft.alignment.center,
                        ),
                        # Monster 2 selector
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.PERSON, size=30, color=ft.Colors.BLUE_400),
                                            ft.Text(
                                                t("monster_2"),
                                                size=TEXT_SIZE_XL,
                                                color=ft.Colors.BLUE_400,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10,
                                    ),
                                    ft.Container(height=SPACING_SM),
                                    monster2_dropdown,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=SPACING_LG,
                            border=ft.border.all(2, ft.Colors.BLUE_400),
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_800,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=SPACING_LG,
                ),
                ft.Container(height=SPACING_XL * 2),
                ft.ElevatedButton(
                    t("view_cards_button"),
                    width=BUTTON_WIDTH_LG,
                    height=BUTTON_HEIGHT_LG,
                    on_click=handle_view_cards,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
    )


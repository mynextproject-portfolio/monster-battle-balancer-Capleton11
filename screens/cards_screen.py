import flet as ft
from dnd_api import get_monster_details
from models.monster import Monster
from ui_constants import (
    SPACING_XS, SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_MD, BUTTON_WIDTH_MD,
    TEXT_SIZE_MD, TEXT_SIZE_LG, TEXT_SIZE_XL,
)


def cards_screen(page: ft.Page, monster1_index: str, monster2_index: str, on_back):
    """Render the two selected monsters as stat cards.

    Args:
        page: The Flet page object
        monster1_index: Index of the first monster
        monster2_index: Index of the second monster
        on_back: Callback function to go back to monster selection
    """
    # Fetch monster details
    monster1 = get_monster_details(monster1_index)
    monster2 = get_monster_details(monster2_index)

    if not monster1 or not monster2:
        # Show error if either monster failed to load
        return ft.Column(
            [
                ft.Container(height=SPACING_XL),
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                ft.Container(height=SPACING_LG),
                ft.Text("モンスター情報の読み込みに失敗しました", size=TEXT_SIZE_XL, color=ft.Colors.RED_400),
                ft.Text("インターネット接続を確認してください", size=TEXT_SIZE_LG, color=ft.Colors.GREY_400),
                ft.Container(height=SPACING_XL),
                ft.ElevatedButton(
                    "← もどる",
                    on_click=on_back,
                    width=BUTTON_WIDTH_MD,
                    height=BUTTON_HEIGHT_MD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def create_monster_card(monster: Monster, color: str) -> ft.Container:
        """Build a single monster stat card (Name, image, HP, AC, Strength)."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        monster.name,
                        size=TEXT_SIZE_XL,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=SPACING_SM),
                    ft.Image(
                        src=monster.image_url if monster.image_url else "",
                        width=180,
                        height=180,
                        fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Icon(ft.Icons.QUESTION_MARK, size=90, color=ft.Colors.GREY_600),
                    ),
                    ft.Container(height=SPACING_SM),
                    # Raw stats block
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"HP: {monster.hp}",
                                    size=TEXT_SIZE_MD,
                                    color=ft.Colors.GREEN_300,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"防御 (AC): {monster.ac}",
                                    size=TEXT_SIZE_MD,
                                    color=ft.Colors.BLUE_300,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"筋力 (STR): {monster.strength}",
                                    size=TEXT_SIZE_MD,
                                    color=ft.Colors.ORANGE_300,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=SPACING_XS,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.BLACK26,
                        border_radius=5,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SPACING_XS,
            ),
            padding=SPACING_SM,
            border=ft.border.all(2, color),
            border_radius=10,
            width=320,
            bgcolor=ft.Colors.GREY_800,
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(height=SPACING_SM),
                # Header: back button + title
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=on_back,
                            tooltip="モンスター選択にもどる",
                        ),
                        ft.Text(
                            "モンスターカード",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(height=SPACING_XL),
                # The two monster cards side by side
                ft.Row(
                    [
                        create_monster_card(monster1, ft.Colors.AMBER_400),
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
                        create_monster_card(monster2, ft.Colors.BLUE_400),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=SPACING_LG,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=SPACING_SM,
    )

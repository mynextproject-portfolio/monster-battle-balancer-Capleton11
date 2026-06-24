import flet as ft
from battle import simulate_battle
from dnd_api import get_monster_details
from i18n import t
from ui_constants import (
    SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_MD, BUTTON_HEIGHT_LG, BUTTON_WIDTH_MD, BUTTON_WIDTH_LG,
    TEXT_SIZE_LG, TEXT_SIZE_XL,
)


def battle_screen(page: ft.Page, monster1_index: str, monster2_index: str, on_back):
    """Fight the two selected monsters and show the winner.

    The combat itself is NOT implemented here — this screen just runs the shared
    simulate_battle engine and displays who won.

    Args:
        page: The Flet page object
        monster1_index: Index of the first monster
        monster2_index: Index of the second monster
        on_back: Callback function to go back to the cards screen
    """
    # Fetch monster details (same approach as the cards screen)
    monster1 = get_monster_details(monster1_index)
    monster2 = get_monster_details(monster2_index)

    if not monster1 or not monster2:
        # Show error if either monster failed to load
        return ft.Column(
            [
                ft.Container(height=SPACING_XL),
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                ft.Container(height=SPACING_LG),
                ft.Text(t("details_load_error"), size=TEXT_SIZE_XL, color=ft.Colors.RED_400),
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

    # Winner name is shown here and refreshed in place when re-fought.
    winner_name = ft.Text(
        size=40,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    def run_fight() -> None:
        """Run one fight via the shared engine and update the winner display.

        Colour the winner's name to match its side (amber for monster 1, blue
        for monster 2). seed is left unset so each fight is a fresh roll.
        """
        winner = simulate_battle(monster1, monster2)
        winner_name.value = winner.name
        winner_name.color = ft.Colors.AMBER_400 if winner is monster1 else ft.Colors.BLUE_400

    def fight_again(e=None) -> None:
        """Re-run the fight and refresh the screen."""
        run_fight()
        page.update()

    # Run the initial fight before the screen is mounted (no page.update needed).
    run_fight()

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
                            tooltip=t("battle_back_tooltip"),
                        ),
                        ft.Text(
                            t("battle_title"),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(height=SPACING_XL),
                # The two combatants, name vs name
                ft.Row(
                    [
                        ft.Text(
                            monster1.name,
                            size=TEXT_SIZE_XL,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.AMBER_400,
                            text_align=ft.TextAlign.CENTER,
                        ),
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
                        ft.Text(
                            monster2.name,
                            size=TEXT_SIZE_XL,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_400,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=SPACING_LG,
                ),
                ft.Container(height=SPACING_XL),
                # Winner announcement
                ft.Icon(ft.Icons.EMOJI_EVENTS, size=80, color=ft.Colors.AMBER_400),
                ft.Text(
                    t("battle_winner_label"),
                    size=TEXT_SIZE_LG,
                    color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                winner_name,
                ft.Container(height=SPACING_XL),
                ft.ElevatedButton(
                    t("fight_again_button"),
                    width=BUTTON_WIDTH_LG,
                    height=BUTTON_HEIGHT_LG,
                    on_click=fight_again,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=SPACING_SM,
    )

import flet as ft
from battle import battle_odds
from dnd_api import get_monster_details
from i18n import t
from ui_constants import (
    SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_MD, BUTTON_HEIGHT_LG, BUTTON_WIDTH_MD, BUTTON_WIDTH_LG,
    TEXT_SIZE_MD, TEXT_SIZE_LG, TEXT_SIZE_XL,
)


def battle_screen(page: ft.Page, monster1_index: str, monster2_index: str, on_back):
    """Show each monster's win chance from many simulated battles.

    The combat and odds are NOT computed here — this screen calls the shared
    battle_odds helper (which runs many simulated battles) and only displays the
    resulting percentages.

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

    # Win-percentage labels and the fun/boring verdict, refreshed in place when
    # re-simulated.
    pct1_text = ft.Text(size=44, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
    pct2_text = ft.Text(size=44, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    verdict_text = ft.Text(
        size=TEXT_SIZE_XL,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    def show_odds(odds) -> None:
        """Display a BattleOdds result (presentation only).

        The fun/boring verdict comes from the logic module (odds.is_fun); the
        screen only maps it to a localized label and colour.
        """
        pct1_text.value = f"{odds.percent1:.1f}%"
        pct2_text.value = f"{odds.percent2:.1f}%"
        verdict_text.value = t("verdict_fun") if odds.is_fun else t("verdict_boring")
        verdict_text.color = ft.Colors.GREEN_400 if odds.is_fun else ft.Colors.GREY_500

    def simulate_again(e=None) -> None:
        """Re-run the simulations and refresh the screen."""
        show_odds(battle_odds(monster1, monster2))
        page.update()

    # Run the initial batch before the screen is mounted (no page.update needed).
    # The result also tells us how many fights to cite in the caption.
    initial_odds = battle_odds(monster1, monster2)
    show_odds(initial_odds)

    def build_side(name: str, pct_text: ft.Text, color: str) -> ft.Container:
        """One monster's column: its name above its win percentage."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        name,
                        size=TEXT_SIZE_XL,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=SPACING_SM),
                    pct_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=260,
            padding=SPACING_LG,
            border=ft.border.all(2, color),
            border_radius=10,
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
                ft.Container(height=SPACING_LG),
                ft.Text(
                    t("win_chance_label"),
                    size=TEXT_SIZE_XL,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_300,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=SPACING_LG),
                # Both monsters' win percentages, side by side
                ft.Row(
                    [
                        build_side(monster1.name, pct1_text, ft.Colors.AMBER_400),
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
                        build_side(monster2.name, pct2_text, ft.Colors.BLUE_400),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=SPACING_LG,
                ),
                ft.Container(height=SPACING_LG),
                # Fun / boring verdict for this matchup
                verdict_text,
                ft.Container(height=SPACING_SM),
                ft.Text(
                    t("battle_runs_caption").format(runs=initial_odds.runs),
                    size=TEXT_SIZE_MD,
                    color=ft.Colors.GREY_500,
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=SPACING_XL),
                ft.ElevatedButton(
                    t("fight_again_button"),
                    width=BUTTON_WIDTH_LG,
                    height=BUTTON_HEIGHT_LG,
                    on_click=simulate_again,
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

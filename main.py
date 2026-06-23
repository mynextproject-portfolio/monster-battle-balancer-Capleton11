import os
import flet as ft
from screens.home_screen import home_screen
from screens.monster_selection_screen import monster_selection_screen
from screens.cards_screen import cards_screen


def main(page: ft.Page):
    """Main application entry point."""
    page.title = "Monster Battle"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Dark theme for D&D atmosphere
    page.bgcolor = ft.Colors.GREY_900
    
    # Desktop screen dimensions
    page.window.width = 1400  # Desktop width
    page.window.height = 900  # Desktop height
    page.window.resizable = True
    page.window.maximizable = True
    
    # Navigation functions
    def navigate_to_home(e=None):
        """Navigate to the home screen."""
        page.clean()
        page.add(home_screen(page, navigate_to_monster_selection))
        page.update()
    
    def navigate_to_monster_selection(e=None):
        """Navigate to the monster selection screen."""
        page.clean()
        page.add(monster_selection_screen(page, navigate_to_home, navigate_to_cards))
        page.update()

    def navigate_to_cards(monster1_index: str, monster2_index: str):
        """Navigate to the cards screen with selected monsters."""
        page.clean()
        page.add(cards_screen(page, monster1_index, monster2_index, navigate_to_monster_selection))
        page.update()
    
    # Start with home screen
    navigate_to_home()


# Local development opens a native desktop window.
# In a container, set FLET_WEB=1 to serve the app over HTTP instead (see Dockerfile).
if os.getenv("FLET_WEB"):
    ft.app(
        main,
        view=None,  # headless: serve as a web app, don't open a desktop window/browser
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )
else:
    ft.app(main)

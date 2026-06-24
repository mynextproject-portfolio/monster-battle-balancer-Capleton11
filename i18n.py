"""
Internationalization (i18n) for the Monster Battle app.

All user-facing UI strings live here, in both Japanese ("ja") and English ("en").
The active language is chosen by the UI_LANG environment variable:

    - Playtester builds: leave UI_LANG unset (or "ja")  -> Japanese UI
    - Developer builds:  set UI_LANG=en in your .env     -> English UI

Japanese is the default on purpose: the playtester session is the critical path,
so a missing or mistyped setting falls back to Japanese rather than silently
shipping English to playtesters. Anyone who wants English opts in explicitly.

To add a new piece of UI text, add the same key to BOTH "ja" and "en" below and
reference it with t("your_key") from the screens.
"""

import os

# Language used when UI_LANG is unset, unknown, or a key is missing.
DEFAULT_LANG = "ja"

TRANSLATIONS = {
    "ja": {
        # App / window
        "app_title": "モンスターバトル",
        # Home screen
        "home_title": "モンスターバトル",
        "home_subtitle": "D&D モンスタービューアー",
        "home_description": "2体のモンスターを選んで、ステータスカードを見比べよう",
        "home_start_button": "モンスターを見る",
        # Shared
        "connection_error": "インターネット接続を確認してください",
        "back_button": "← もどる",
        # Monster selection screen
        "monsters_load_error": "モンスターの読み込みに失敗しました",
        "selection_title": "モンスター選択",
        "selection_back_tooltip": "ホームにもどる",
        "selection_instruction": "見比べる2体のモンスターを選んでください",
        "select_monster_1": "モンスター1を選択",
        "select_monster_2": "モンスター2を選択",
        "monster_1": "モンスター1",
        "monster_2": "モンスター2",
        "select_two_warning": "モンスターを2体選んでください！",
        "view_cards_button": "🃏 カードを見る",
        # Cards screen
        "details_load_error": "モンスター情報の読み込みに失敗しました",
        "cards_title": "モンスターカード",
        "cards_back_tooltip": "モンスター選択にもどる",
        "stat_hp": "HP",
        "stat_ac": "防御 (AC)",
        "stat_str": "筋力 (STR)",
        "fight_button": "⚔️ バトル開始",
        # Battle screen
        "battle_title": "バトル",
        "battle_back_tooltip": "カードにもどる",
        "battle_winner_label": "勝者",
        "fight_again_button": "🔄 もう一度たたかう",
    },
    "en": {
        # App / window
        "app_title": "Monster Battle",
        # Home screen
        "home_title": "Monster Battle",
        "home_subtitle": "D&D Monster Viewer",
        "home_description": "Pick two monsters and compare their stat cards",
        "home_start_button": "Browse Monsters",
        # Shared
        "connection_error": "Please check your internet connection",
        "back_button": "← Back",
        # Monster selection screen
        "monsters_load_error": "Failed to load monsters",
        "selection_title": "Select Monsters",
        "selection_back_tooltip": "Back to Home",
        "selection_instruction": "Choose two monsters to compare",
        "select_monster_1": "Select Monster 1",
        "select_monster_2": "Select Monster 2",
        "monster_1": "Monster 1",
        "monster_2": "Monster 2",
        "select_two_warning": "Please select two monsters!",
        "view_cards_button": "🃏 View Cards",
        # Cards screen
        "details_load_error": "Failed to load monster details",
        "cards_title": "Monster Cards",
        "cards_back_tooltip": "Back to Monster Selection",
        "stat_hp": "HP",
        "stat_ac": "Armor Class (AC)",
        "stat_str": "Strength (STR)",
        "fight_button": "⚔️ Start Battle",
        # Battle screen
        "battle_title": "Battle",
        "battle_back_tooltip": "Back to Cards",
        "battle_winner_label": "Winner",
        "fight_again_button": "🔄 Fight Again",
    },
}


def get_language() -> str:
    """Return the active UI language code, falling back to DEFAULT_LANG.

    Read lazily (per call) so the language can be set via the environment
    without needing to restart the import chain.
    """
    lang = os.getenv("UI_LANG", DEFAULT_LANG).strip().lower()
    return lang if lang in TRANSLATIONS else DEFAULT_LANG


def t(key: str) -> str:
    """Look up a UI string by key for the active language.

    Falls back to the default language, then to the key itself, so a missing
    translation degrades gracefully instead of crashing the UI.
    """
    strings = TRANSLATIONS.get(get_language(), TRANSLATIONS[DEFAULT_LANG])
    if key in strings:
        return strings[key]
    return TRANSLATIONS[DEFAULT_LANG].get(key, key)

"""Translation system ported from CSGO-API/services/translations.js."""
import re

from api_gen.constants import CUSTOM_TRANSLATIONS


class Translations:
    def __init__(self):
        self.default: dict[str, str] = {}
        self.default_idx: list[str] = []
        self.selected: dict[str, str] = {}
        self.selected_idx: list[str] = []
        self.language: str = "en"

    def load_from_dict(self, default: dict[str, str], selected: dict[str, str]) -> None:
        self.default = {k.lower(): v for k, v in default.items()}
        self.default_idx = list(self.default.keys())
        self.selected = {k.lower(): v for k, v in selected.items()}
        self.selected_idx = list(self.selected.keys())

    def load_from_json(self, default_data: dict, selected_data: dict) -> None:
        """Load from parsed csgo_english.json format: {lang: {Tokens: {...}}}"""
        default_tokens = default_data.get("lang", {}).get("Tokens", {})
        selected_tokens = selected_data.get("lang", {}).get("Tokens", {})
        self.load_from_dict(default_tokens, selected_tokens)

    def set_language(self, lang: str) -> None:
        self.language = lang

    def t(self, key: str | None, use_default: bool = False) -> str | None:
        if key is None:
            return None
        key = key.replace("#", "", 1).lower()
        if use_default:
            return self.default.get(key)
        return self.selected.get(key) or self.default.get(key)

    def t_tag(self, key: str | None, use_default: bool = False) -> str | None:
        if key is None:
            return None
        key = key.replace("#", "", 1).lower()
        target = self.default if use_default else self.selected
        target_idx = self.default_idx if use_default else self.selected_idx

        try:
            search = target_idx.index(key)
        except ValueError:
            return None

        for i in range(search, -1, -1):
            if "_tag" not in target_idx[i].lower():
                return target[target_idx[i]]
        return None

    def tc(self, key: str, data: dict[str, str] | None = None) -> str:
        folder = self.language
        all_trans = CUSTOM_TRANSLATIONS.get(folder)
        if not all_trans:
            raise ValueError(f"Translations for '{folder}' not found")

        template = all_trans.get(key)
        if not template:
            raise ValueError(f"Key '{key}' not in '{folder}' translations")

        if data is None:
            return template

        def replacer(match):
            k = match.group(1)
            if k not in data:
                raise ValueError(f"$tc data key {{{k}}} not provided")
            return str(data[k])

        return re.sub(r"\{(.+?)\}", replacer, template)

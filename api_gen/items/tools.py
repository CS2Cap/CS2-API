from __future__ import annotations

from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations


def generate_tools(state: State, translations: Translations) -> list[dict]:
    cdn = state.cdn_images

    tools = [
        {
            "id": "tool-1",
            "name": translations.t("csgo_tool_name_tag"),
            "description": translations.t("csgo_tool_name_tag_desc"),
            "image": cdn.get("econ/tools/tag") or get_image_url("econ/tools/tag"),
            "def_index": "1200",
            "original": {
                "image_inventory": "econ/tools/tag",
            },
        },
        {
            "id": "tool-2",
            "name": translations.t("csgo_tool_casket_tag"),
            "description": translations.t("csgo_tool_casket_tag_desc"),
            "image": cdn.get("econ/tools/casket") or get_image_url("econ/tools/casket"),
            "def_index": "1201",
            "original": {
                "image_inventory": "econ/tools/casket",
            },
        },
        {
            "id": "tool-3",
            "name": translations.t("csgo_tool_stattrak_swap"),
            "description": translations.t("csgo_tool_stattrak_swap_desc"),
            "image": cdn.get("econ/tools/stattrak_swap_tool") or get_image_url("econ/tools/stattrak_swap_tool"),
            "def_index": "1324",
            "original": {
                "image_inventory": "econ/tools/stattrak_swap_tool",
            },
        },
        {
            "id": "tool-4",
            "name": translations.t("csgo_removekeychainTool_title"),
            "description": translations.t("csgo_removekeychaintool_desc"),
            "image": cdn.get("econ/tools/keychain_remove_tool") or get_image_url("econ/tools/keychain_remove_tool"),
            "def_index": "4950",
            "original": {
                "image_inventory": "econ/tools/keychain_remove_tool",
            },
        },
    ]

    return tools

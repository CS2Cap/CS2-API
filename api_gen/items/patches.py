from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color


def _is_patch(item: dict) -> bool:
    """Return True if *item* is a real patch sticker kit."""
    if item.get("patch_material") == "case_skillgroups/patch_legendaryeagle":
        return False
    return item.get("patch_material") is not None


def _get_description(item: dict, translations: Translations) -> str:
    """Build the patch description string, optionally appending item-specific text."""
    msg = translations.t("CSGO_Tool_Patch_Desc") or ""
    desc = translations.t(item.get("description_string"))
    if desc and len(desc) > 0:
        msg = f"{msg}<br><br>{desc}"
    return msg


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    patch_material = item.get("patch_material", "")
    image_key = f"econ/patches/{patch_material}"
    image = state.cdn_images.get(image_key) or get_image_url(image_key)

    rarity_key = f"rarity_{item.get('item_rarity', '')}"

    return {
        "id": f"patch-{item['object_id']}",
        "name": f"{translations.t('csgo_tool_patch')} | {translations.t(item.get('item_name'))}",
        "description": _get_description(item, translations),
        "def_index": item["object_id"],
        "rarity": {
            "id": rarity_key,
            "name": translations.t(rarity_key),
            "color": get_rarity_color(rarity_key),
        },
        "market_hash_name": (
            f"{translations.t('csgo_tool_patch', use_default=True)}"
            f" | {translations.t(item.get('item_name'), use_default=True)}"
        ),
        "image": image,

        "original": {
            "name": item.get("name"),
            "image_inventory": image_key,
        },
    }


def generate_patches(state: State, translations: Translations) -> list[dict]:
    return [
        _parse_item(item, state, translations)
        for item in state.sticker_kits
        if _is_patch(item)
    ]

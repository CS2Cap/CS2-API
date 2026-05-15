from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color


def _is_keychain(item: dict) -> bool:
    """Return True if *item* is a tradable keychain definition."""
    if not item.get("loc_name", "").startswith("#keychain_"):
        return False
    if item.get("is commodity"):
        return False
    return True


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    image_inventory = item.get("image_inventory", "").lower()
    image = state.cdn_images.get(image_inventory) or get_image_url(image_inventory)

    rarity_key = f"rarity_{item.get('item_rarity', '')}"

    keychain_id = f"keychain-{item['object_id']}"

    raw_collections = state.collections_by_skins.get(keychain_id, [])
    collections = [
        {**col, "name": translations.t(col["name"])}
        for col in raw_collections
    ]

    return {
        "id": keychain_id,
        "name": (
            f"{translations.t('CSGO_Tool_Keychain')}"
            f" | {translations.t(item.get('loc_name'))}"
        ),
        "description": translations.t("csgo_tool_keychain_desc"),
        "def_index": item["object_id"],
        "rarity": {
            "id": rarity_key,
            "name": translations.t(rarity_key),
            "color": get_rarity_color(rarity_key),
        },
        "collections": collections,
        "market_hash_name": (
            f"{translations.t('CSGO_Tool_Keychain', use_default=True)}"
            f" | {translations.t(item.get('loc_name'), use_default=True)}"
        ),
        "image": image,
        "original": {
            "loc_name": item.get("loc_name"),
            "image_inventory": image_inventory,
        },
    }


def generate_keychains(state: State, translations: Translations) -> list[dict]:
    return [
        _parse_item(item, state, translations)
        for item in state.keychain_definitions
        if _is_keychain(item)
    ]

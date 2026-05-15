from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations

# Keys that are tradable on the Steam Market
_MARKETABLE_ITEM_NAMES = {
    "#CSGO_Tool_WeaponCase_Key",
    "#CSGO_esports_crate_key_1",
    "#CSGO_sticker_crate_key_1",
    "#CSGO_community_crate_key_1",
    "#CSGO_community_crate_key_2",
    "#CSGO_sticker_crate_key_community01",
    "#CSGO_community_crate_key_3",
    "#CSGO_community_crate_key_4",
    "#CSGO_community_crate_key_5",
    "#CSGO_community_crate_key_6",
    "#CSGO_community_crate_key_7",
    "#CSGO_community_crate_key_8",
    "#CSGO_community_crate_key_9",
    "#CSGO_crate_community_10_key",
    "#CSGO_crate_key_community_11",
    "#CSGO_crate_key_community_12",
    "#CSGO_crate_key_community_13",
    "#CSGO_crate_key_gamma_2",
    "#CSGO_crate_key_community_15",
    "#CSGO_crate_key_community_16",
    "#CSGO_crate_key_community_17",
    "#CSGO_crate_key_community_18",
    "#CSGO_crate_key_community_19",
    "#CSGO_crate_key_community_20",
    "#CSGO_crate_key_community_21",
    "#CSGO_crate_key_community_22",
    "#CSGO_crate_key_community_24",
}

# Hardcoded generic Valve key that doesn't appear in items_game items
_GENERIC_VALVE_KEY = {
    "object_id": "1203",
    "item_name": "#CSGO_Tool_WeaponCase_Key",
    "item_description": "#CSGO_Tool_WeaponCase_Key_Desc",
    "image_inventory": "econ/tools/weapon_case_key",
    "tool": {
        "restriction": "generic_valve_key",
    },
}


def _is_key(item: dict) -> bool:
    """Return True if *item* is a weapon case key."""
    item_name = item.get("item_name")
    if item_name is None:
        return False
    if "contestwinner" in item_name:
        return False
    if "storepromo_key" in item_name:
        return False
    prefab = item.get("prefab") or ""
    return "weapon_case_key" in prefab


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    image_inventory = (item.get("image_inventory") or "").lower()
    image = state.cdn_images.get(image_inventory) or get_image_url(image_inventory)

    item_name = item.get("item_name")
    item_tool = item.get("tool") or {}

    # Find crates that this key opens
    key_restriction = item_tool.get("restriction")
    crates = []
    for crate in state.items.values():
        crate_prefab = crate.get("prefab") or ""
        if crate_prefab not in ("sticker_capsule", "weapon_case"):
            continue
        crate_tool = crate.get("tool") or {}
        if crate_tool.get("restriction") != key_restriction:
            continue
        crate_img_inv = (crate.get("image_inventory") or "").lower()
        crates.append({
            "id": f"crate-{crate['object_id']}",
            "name": translations.t(crate.get("item_name")),
            "image": state.cdn_images.get(crate_img_inv) or get_image_url(crate_img_inv),
        })

    marketable = item_name in _MARKETABLE_ITEM_NAMES

    return {
        "id": f"key-{item['object_id']}",
        "name": translations.t(item_name),
        "description": (
            translations.t(item.get("item_description"))
            or translations.t(item.get("item_description_prefab"))
        ),
        "def_index": item["object_id"],
        "crates": crates,
        "market_hash_name": translations.t(item_name, use_default=True) if marketable else None,
        "marketable": marketable,
        "image": image,

        "original": {
            "item_name": item_name,
            "image_inventory": image_inventory,
        },
    }


def generate_keys(state: State, translations: Translations) -> list[dict]:
    raw_items = [_GENERIC_VALVE_KEY] + [
        item for item in state.items.values() if _is_key(item)
    ]

    seen: dict[str, bool] = {}
    result = []
    for item in raw_items:
        parsed = _parse_item(item, state, translations)
        # Deduplicate by image URL
        img = parsed["image"]
        if seen.get(img):
            continue
        seen[img] = True
        if parsed["name"]:
            result.append(parsed)

    return result

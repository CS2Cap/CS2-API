from __future__ import annotations

from api_gen.constants import get_image_url, get_image_url_svg
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color

_SPECIAL_COLLECTIONS = [
    "#CSGO_set_timed_drops_achroma",
    "#CSGO_set_timed_drops_exuberant",
]


def _get_collection_image(collection_name: str, image_path: str, cdn_images: dict) -> str:
    """Return the best available image URL for a collection."""
    if image_path in cdn_images:
        return cdn_images[image_path]
    if collection_name in _SPECIAL_COLLECTIONS:
        return get_image_url_svg(image_path)
    return get_image_url(image_path)


def _is_collection(item: dict) -> bool:
    """Return True if this item_set entry is a collection."""
    return item.get("is_collection") is not None


def _is_self_opening_collection(item: dict) -> bool:
    """Return True if this items entry is a self-opening graffiti collection."""
    item_name = item.get("item_name")
    if item_name is None:
        return False

    if not item_name.startswith("#CSGO_crate"):
        return False

    if "#CSGO_crate_tool_stattrak_swap" in item_name:
        return False

    prefab = item.get("prefab") or ""
    if "weapon_case_key" in prefab:
        return False

    if item.get("item_type") == "self_opening_purchase":
        if "graffiti" in prefab:
            return True

    return False


def _resolve_item_name(i: dict, translations: Translations) -> str | None:
    """Resolve the display name from a skins_by_collections entry."""
    name = i.get("name")
    if isinstance(name, dict):
        weapon = translations.t(name.get("weapon"))
        pattern = translations.t(name.get("pattern"))
        return f"{weapon} | {pattern}"
    return translations.t(name)


def _parse_item_set(item: dict, state: State, translations: Translations) -> dict:
    """Parse a standard item set (has is_collection flag)."""
    cdn_images = state.cdn_images
    skins_by_collections = state.skins_by_collections
    crates_by_collections = state.crates_by_collections

    file_name = item.get("name", "").replace("#CSGO_", "")
    image_inventory = f"econ/set_icons/{file_name}"
    image = _get_collection_image(item.get("name", ""), image_inventory, cdn_images)

    collection_id = f"collection-{file_name.replace('_', '-')}"

    name_key = item.get("name_force") or item.get("name")
    name = translations.t(name_key)

    raw_crates = crates_by_collections.get(file_name, [])
    crates = [
        {**c, "name": translations.t(c["name"])}
        for c in raw_crates
    ]

    raw_skins = skins_by_collections.get(file_name, [])
    contains = []
    for i in raw_skins:
        rarity_id = i.get("rarity")
        contains.append({
            **i,
            "name": _resolve_item_name(i, translations),
            "rarity": {
                "id": rarity_id,
                "name": translations.t(rarity_id),
                "color": get_rarity_color(rarity_id),
            },
        })

    return {
        "id": collection_id,
        "name": name,
        "crates": crates,
        "contains": contains,
        "image": image,

        "original": {
            "name": item.get("name"),
            "image_inventory": image_inventory,
        },
    }


def _parse_self_opening_item(item: dict, state: State, translations: Translations) -> dict:
    """Parse a self-opening graffiti collection item."""
    cdn_images = state.cdn_images
    skins_by_collections = state.skins_by_collections

    image_inventory = (item.get("image_inventory") or "").lower()
    image = cdn_images.get(image_inventory) or get_image_url(image_inventory)

    raw_skins = skins_by_collections.get(item.get("name", ""), [])
    contains = []
    for i in raw_skins:
        rarity_id = i.get("rarity")
        contains.append({
            **i,
            "name": translations.t(i.get("name")),
            "rarity": {
                "id": rarity_id,
                "name": translations.t(rarity_id),
                "color": get_rarity_color(rarity_id),
            },
        })

    return {
        "id": f"collection-{item['object_id']}",
        "name": translations.t(item.get("item_name")),
        "crates": [],
        "contains": contains,
        "image": image,

        "original": {
            "name": item.get("name"),
            "item_name": item.get("item_name"),
            "image_inventory": image_inventory,
        },
    }


def generate_collections(state: State, translations: Translations) -> list[dict]:
    """Return the full collections list, combining item sets and self-opening items."""
    collections: list[dict] = []

    for item in state.item_sets:
        if _is_collection(item):
            parsed = _parse_item_set(item, state, translations)
            if parsed["name"]:
                collections.append(parsed)

    for item in state.items.values():
        if _is_self_opening_collection(item):
            parsed = _parse_self_opening_item(item, state, translations)
            if parsed["name"]:
                collections.append(parsed)

    return collections

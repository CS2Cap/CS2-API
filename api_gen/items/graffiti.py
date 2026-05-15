from api_gen.constants import SPECIAL_NOTES, get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_graffiti_variations, get_rarity_color


def _is_graffiti(item: dict) -> bool:
    """Return True if *item* is a graffiti sticker kit."""
    item_name = item.get("item_name", "")
    if item_name.startswith("#SprayKit_"):
        return True
    name = item.get("name", "")
    if "spray_" in name:
        return True
    sticker_material = item.get("sticker_material") or ""
    if "_graffiti" in sticker_material:
        return True
    return False


def _get_description(item: dict, translations: Translations) -> str:
    """Build the graffiti description, optionally appending item-specific text."""
    msg = translations.t("csgo_tool_spray_desc") or ""
    desc = translations.t(item.get("description_string"))
    if desc and len(desc) > 0:
        msg = f"{msg}<br><br>{desc}"
    return msg


def _get_market_hash_name(item: dict, color_key: str | None, translations: Translations) -> str | None:
    """Return the Steam market hash name for a graffiti item or color variant."""
    if color_key:
        return (
            f"{translations.t('csgo_tool_spray', use_default=True)}"
            f" | {translations.t(item.get('item_name'), use_default=True)}"
            f" ({translations.t(color_key, use_default=True)})"
        )
    # Only tournament_event_id 11, 12, 13, 14 have market hash names 
    tournament_event_id = item.get("tournament_event_id")
    if tournament_event_id and tournament_event_id not in (11, 12, 13, 14):
        return None
    return (
        f"{translations.t('csgo_tool_spray', use_default=True)}"
        f" | {translations.t(item.get('item_name'), use_default=True)}"
    )


def _parse_item(item: dict, state: State, translations: Translations) -> list[dict]:
    """Parse a graffiti sticker kit into one or more output dicts."""
    sticker_material = item.get("sticker_material", "")
    image_key = f"econ/stickers/{sticker_material}"
    image = state.cdn_images.get(image_key) or get_image_url(image_key)

    rarity_key = f"rarity_{item.get('item_rarity', '')}"
    rarity = {
        "id": rarity_key,
        "name": translations.t(rarity_key),
        "color": get_rarity_color(rarity_key),
    }

    graffiti_id = f"graffiti-{item['object_id']}"
    special_notes = SPECIAL_NOTES.get(graffiti_id)

    # Look up crates for this graffiti (keyed without color suffix)
    raw_crates = state.crates_by_skins.get(graffiti_id, [])
    crates = [
        {**crate, "name": translations.t(crate["name"])}
        for crate in raw_crates
    ]

    name = item.get("name", "")
    variations = get_graffiti_variations(name)

    # If variations == [0], use the full range 1-19; otherwise use the list as-is.
    if variations == [0]:
        variation_indices = list(range(1, 20))
    else:
        variation_indices = variations

    if variation_indices:
        result = []
        for index in variation_indices:
            color_key = f"attrib_spraytintvalue_{index}"
            colored_image_key = f"econ/stickers/{sticker_material}_{index}"
            result.append({
                "id": f"{graffiti_id}_{index}",
                "name": (
                    f"{translations.t('csgo_tool_spray')}"
                    f" | {translations.t(item.get('item_name'))}"
                    f" ({translations.t(color_key)})"
                ),
                "description": _get_description(item, translations),
                "def_index": item["object_id"],
                "color_index": index,
                "rarity": rarity,
                "special_notes": special_notes,
                "crates": crates,
                "market_hash_name": _get_market_hash_name(item, color_key, translations),
                "image": (
                    state.cdn_images.get(colored_image_key)
                    or get_image_url(colored_image_key)
                ),
                "original": {
                    "item_name": item.get("item_name"),
                    "image_inventory": colored_image_key,
                },
            })
        return result

    return [{
        "id": graffiti_id,
        "name": (
            f"{translations.t('csgo_tool_spray')}"
            f" | {translations.t(item.get('item_name'))}"
        ),
        "description": _get_description(item, translations),
        "def_index": item["object_id"],
        "rarity": rarity,
        "special_notes": special_notes,
        "crates": crates,
        "market_hash_name": _get_market_hash_name(item, None, translations),
        "image": image,
        "original": {
            "name": item.get("name"),
            "image_inventory": image_key,
        },
    }]


def generate_graffiti(state: State, translations: Translations) -> list[dict]:
    result: list[dict] = []
    for item in state.sticker_kits:
        if _is_graffiti(item):
            result.extend(_parse_item(item, state, translations))
    return result

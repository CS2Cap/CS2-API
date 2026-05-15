from __future__ import annotations

from api_gen.constants import SPECIAL_NOTES, get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color

# Object IDs whose crates should NOT have a market_hash_name
_NO_MARKET_HASH_NAME_IDS = {
    "4600", "4614", "4719", "4729", "4779", "4871", "4872", "4783", "4795",
}


def _is_crate(item: dict) -> bool:
    """Return True if this item entry is a crate/capsule/case."""
    item_name = item.get("item_name")
    if item_name is None:
        return False

    # Storage units with supply crate series attribute
    attributes = item.get("attributes") or {}
    supply_crate = attributes.get("set supply crate series") or {}
    if supply_crate.get("attribute_class") == "supply_crate_series":
        return True

    # Storage units by name
    if item_name.startswith("#CSGO_storageunit"):
        return True

    if not item_name.startswith("#CSGO_crate"):
        return False

    if "#CSGO_crate_tool_stattrak_swap" in item_name:
        return False

    prefab = item.get("prefab") or ""
    if "weapon_case_key" in prefab:
        return False

    if item.get("item_type") == "self_opening_purchase":
        return False

    return True


def _get_crate_type(item: dict) -> str | None:
    """Determine the display type of a crate from its prefab/name."""
    prefab = item.get("prefab") or ""
    item_name = item.get("item_name") or ""
    name = item.get("name") or ""
    image_inventory = item.get("image_inventory") or ""

    if prefab == "weapon_case":
        return "Case"

    if prefab == "weapon_case_souvenirpkg" or "souvenir_crate" in prefab:
        return "Souvenir"

    if item_name.startswith("#CSGO_storageunit"):
        return None

    if "sticker_capsule" in prefab:
        return "Sticker Capsule"

    if prefab == "graffiti_box":
        return "Graffiti"

    if name.startswith("crate_pins"):
        return "Pins"

    if name.startswith("crate_signature"):
        return "Autograph Capsule"

    if "patch" in image_inventory:
        return "Patch Capsule"

    if name.startswith("crate_musickit"):
        return "Music Kit Box"

    tags = item.get("tags") or {}
    if "StickerCapsule" in tags:
        return "Sticker Capsule"

    return None


def _get_first_sale_date(item: dict, prefabs: dict, items_game_items: dict) -> str | None:
    """Return the first_sale_date for a crate, checking item then associated_items then prefab."""
    if item.get("first_sale_date") is not None:
        return item["first_sale_date"]

    associated_items = item.get("associated_items")
    if associated_items is not None:
        first_id = next(iter(associated_items), None)
        if first_id is not None:
            raw_item = items_game_items.get(first_id)
            if raw_item is not None:
                return raw_item.get("first_sale_date")

    prefab = item.get("prefab")
    if prefab is not None:
        return (prefabs.get(prefab) or {}).get("first_sale_date")

    return None


def _get_market_hash_name(item: dict, translations: Translations) -> str | None:
    """Return the Steam market hash name, or None for excluded/untradable crates."""
    object_id = str(item.get("object_id", ""))
    if object_id in _NO_MARKET_HASH_NAME_IDS:
        return None
    name = translations.t(item.get("item_name"), use_default=True)
    if name is None:
        return None
    return name.replace("Holo/Foil", "Holo-Foil")


def _resolve_contains_name(i: dict, translations: Translations) -> str | None:
    """Resolve the display name for a contains entry."""
    name = i.get("name")
    if isinstance(name, dict):
        weapon = translations.t(name.get("weapon"))
        pattern = translations.t(name.get("pattern"))
        return f"{weapon} | {pattern}"
    return translations.t(name)


def _resolve_rare_name(i: dict, translations: Translations) -> str | None:
    """Resolve the display name for a contains_rare entry using tc() or t()."""
    name = i.get("name")
    if not isinstance(name, dict):
        return translations.t(name)

    t_key = name.get("tKey")
    weapon_key = name.get("weapon")
    pattern_key = name.get("pattern")

    # Use the tKey template if available, else fall back to plain translation
    if t_key:
        try:
            return translations.tc(
                t_key,
                {
                    "item_name": translations.t(weapon_key) or "",
                    "pattern": translations.t(pattern_key) or "",
                },
            )
        except (ValueError, KeyError):
            pass

    # Fallback: weapon | pattern
    weapon = translations.t(weapon_key)
    pattern = translations.t(pattern_key)
    if weapon and pattern:
        return f"{weapon} | {pattern}"
    return weapon or pattern


def _parse_item(
    item: dict,
    state: State,
    translations: Translations,
    prefabs: dict,
    items_game_items: dict,
) -> dict | list[dict]:
    """Parse a single crate item into one or two output dicts."""
    skins_by_crates = state.skins_by_crates
    revolving_loot_lists = state.revolving_loot_lists
    cdn_images = state.cdn_images

    image_inventory = (item.get("image_inventory") or "").lower()
    image = cdn_images.get(image_inventory) or get_image_url(image_inventory)

    loot_list_name = item.get("loot_list_name") or None
    attributes = item.get("attributes") or {}
    attribute_value = (attributes.get("set supply crate series") or {}).get("value") or None
    key_loot_list = loot_list_name or revolving_loot_lists.get(attribute_value) or None

    tags = item.get("tags") or {}
    item_set_tag = (tags.get("ItemSet") or {}).get("tag_value")

    # Build contains list
    raw_contains = (
        skins_by_crates.get(item_set_tag)
        if item_set_tag and item_set_tag in skins_by_crates
        else skins_by_crates.get(key_loot_list, [])
    ) or []

    contains = []
    for i in raw_contains:
        rarity_id = i.get("rarity")
        contains.append({
            **i,
            "name": _resolve_contains_name(i, translations),
            "rarity": {
                "id": rarity_id,
                "name": translations.t(rarity_id),
                "color": get_rarity_color(rarity_id),
            },
        })

    # Build contains_rare list
    raw_rare = skins_by_crates.get(f"rare--{key_loot_list}", []) if key_loot_list else []
    contains_rare = []
    for i in raw_rare:
        rarity_id = i.get("rarity")
        contains_rare.append({
            **i,
            "name": _resolve_rare_name(i, translations),
            "rarity": {
                "id": rarity_id,
                "name": translations.t(rarity_id),
                "color": get_rarity_color(rarity_id),
            },
        })

    object_id = str(item.get("object_id", ""))

    # loot_list block
    loot_list_rare_item_name = item.get("loot_list_rare_item_name")
    if loot_list_rare_item_name:
        loot_list_block: dict | None = {
            "name": translations.t(loot_list_rare_item_name),
            "footer": translations.t(item.get("loot_list_rare_item_footer")),
            # Crates without image_unusual_item have gloves
            "image": (
                get_image_url(item["image_unusual_item"])
                if item.get("image_unusual_item")
                else get_image_url("econ/weapon_cases/default_rare_item")
            ),
        }
    else:
        loot_list_block = None

    crate = {
        "id": f"crate-{object_id}",
        "name": translations.t(item.get("item_name")),
        "description": (
            translations.t(item.get("item_description"))
            or translations.t(item.get("item_description_prefab"))
        ),
        "def_index": object_id,
        "type": _get_crate_type(item),
        "first_sale_date": _get_first_sale_date(item, prefabs, items_game_items),
        "rarity": {
            "id": "rarity_common",
            "name": translations.t("rarity_common"),
            "color": get_rarity_color("rarity_common"),
        },
        "contains": contains,
        "contains_rare": contains_rare,
        "special_notes": SPECIAL_NOTES.get(f"crate-{object_id}"),
        "market_hash_name": _get_market_hash_name(item, translations),
        "rental": bool(attributes.get("can open for rental")),
        "image": image,
        "model_player": item.get("model_player") or None,
        "loot_list": loot_list_block,

        "original": {
            "item_name": item.get("item_name"),
            "image_inventory": image_inventory,
        },
    }

    # Souvenir Highlight Package variant
    highlight_key = f"{item.get('item_name')}^highlight"
    highlight_name = translations.t(highlight_key)
    if highlight_name:
        highlight_market_hash = translations.t(highlight_key, use_default=True)
        highlight_crate = {
            **crate,
            "id": f"crate-{object_id}_highlight",
            "name": highlight_name,
            "rarity": {
                "id": "rarity_common_highlight",
                "name": f"{translations.t('highlight')} {translations.t('rarity_common')}",
                "color": "#ffd7aa",  # Highlight Base Grade Container
            },
            "type": "Souvenir Highlight",
            "market_hash_name": highlight_market_hash,
        }
        return [crate, highlight_crate]

    return crate


def generate_crates(
    state: State,
    translations: Translations,
) -> list[dict]:
    """Return the full crates list."""
    prefabs = state.prefabs
    items_game_items = state.items_game.get("items", {})

    result: list[dict] = []
    for item in state.items.values():
        if not _is_crate(item):
            continue

        parsed = _parse_item(item, state, translations, prefabs, items_game_items)

        if isinstance(parsed, list):
            for p in parsed:
                if p.get("name"):
                    result.append(p)
        else:
            if parsed.get("name"):
                result.append(parsed)

    return result

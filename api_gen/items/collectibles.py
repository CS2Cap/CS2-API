from __future__ import annotations

from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_collectible_rarity, get_rarity_color


def _is_collectible(item: dict) -> bool:
    item_name = item.get("item_name")
    if item_name is None:
        return False
    if item_name.startswith("#CSGO_Collectible"):
        return True
    if item_name.startswith("#CSGO_TournamentJournal"):
        return True
    if item_name.startswith("#CSGO_TournamentPass") or item_name.startswith("#CSGO_Ticket_"):
        return True
    return False


def _get_type(item: dict) -> str | None:
    image_inventory = item.get("image_inventory", "")
    item_name = item.get("item_name", "")
    prefab = item.get("prefab") or ""
    attributes = item.get("attributes") or {}

    if "service_medal" in image_inventory:
        return "Service Medal"

    if item_name.startswith("#CSGO_Collectible_Map"):
        return "Map Contributor Coin"

    if item_name.startswith("#CSGO_TournamentJournal"):
        return "Pick'Em Coin"

    if item_name.startswith("#CSGO_Collectible_Pin"):
        return "Pin"

    if item_name.startswith("#CSGO_TournamentPass") and item_name.endswith("_charge"):
        return "Souvenir Token"

    if item_name.startswith("#CSGO_TournamentPass"):
        return "Tournament Pass"

    if item_name.startswith("#CSGO_Ticket_"):
        return "Operation Pass"

    if item_name.startswith("#CSGO_Collectible_CommunitySeason"):
        if prefab == "valve season_tiers":
            return "Stars for Operation"
        return "Operation Coin"

    if attributes.get("tournament event id") is not None:
        if "PickEm" in item_name:
            return "Old Pick'Em Trophy"
        if "Fantasy" in item_name:
            return "Fantasy Trophy"
        return "Tournament Finalist Trophy"

    if prefab == "premier_season_coin":
        return "Premier Season Coin"

    return None


def _get_market_hash_name(item: dict, translations: Translations) -> str | None:
    is_attendance = item.get("prefab") == "attendance_pin"
    attributes = item.get("attributes") or {}
    is_cannot_trade = attributes.get("cannot trade")

    if is_cannot_trade:
        return None

    item_type = _get_type(item)
    if item_type in ("Pin", "Souvenir Token", "Tournament Pass", "Operation Pass") and not is_attendance:
        return translations.t(item.get("item_name"), use_default=True)

    return None


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    is_attendance = item.get("prefab") == "attendance_pin"
    image_inventory = item.get("image_inventory", "")
    image = state.cdn_images.get(image_inventory) or get_image_url(image_inventory)

    item_rarity = item.get("item_rarity")
    if item_rarity:
        rarity_id = f"rarity_{item_rarity}"
    else:
        rarity_id = get_collectible_rarity(item.get("prefab") or "")

    if is_attendance:
        name = translations.tc(
            "collectible_genuine",
            {
                "genuine": translations.t("genuine"),
                "item_name": translations.t(item.get("item_name")),
            },
        )
    else:
        name = translations.t(item.get("item_name"))

    item_description = item.get("item_description")
    item_description_prefab = item.get("item_description_prefab")
    if item_description:
        description = translations.t(item_description)
    elif item_description_prefab:
        description = translations.t(item_description_prefab)
    else:
        description = None

    attributes = item.get("attributes") or {}
    premier_season = attributes.get("premier season")

    return {
        "id": f"collectible-{item['object_id']}",
        "name": name,
        "description": description,
        "def_index": item["object_id"],
        "rarity": {
            "id": rarity_id,
            "name": translations.t(rarity_id),
            "color": get_rarity_color(rarity_id),
        },
        "type": _get_type(item),
        "genuine": is_attendance,
        "premier_season": premier_season,
        "market_hash_name": _get_market_hash_name(item, translations),
        "image": image,
        "original": {
            "item_name": item.get("item_name"),
            "image_inventory": image_inventory,
        },
    }


def generate_collectibles(state: State, translations: Translations) -> list[dict]:
    result = []
    for item in state.items.values():
        if not _is_collectible(item):
            continue
        parsed = _parse_item(item, state, translations)
        if parsed["name"]:
            result.append(parsed)
    return result

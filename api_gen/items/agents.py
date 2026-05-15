from __future__ import annotations

from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    name_lower = item.get("name", "").lower()
    image_key = f"econ/characters/{name_lower}"
    image = state.cdn_images.get(image_key) or get_image_url(image_key)

    item_rarity = item.get("item_rarity", "")
    rarity_id = f"rarity_{item_rarity}_character"

    agent_id = f"agent-{item['object_id']}"

    raw_collections = state.collections_by_skins.get(agent_id)
    if raw_collections is not None:
        collections = [
            {**col, "name": translations.t(col["name"])}
            for col in raw_collections
        ]
    else:
        collections = None

    used_by_classes = item.get("used_by_classes") or {}
    team_id = next(iter(used_by_classes), None)
    if team_id == "counter-terrorists":
        team_name = translations.t("inv_filter_ct")
    else:
        team_name = translations.t("inv_filter_t")

    return {
        "id": agent_id,
        "name": translations.t(item.get("item_name")),
        "description": translations.t(item.get("item_description")),
        "def_index": item["object_id"],
        "rarity": {
            "id": rarity_id,
            "name": translations.t(rarity_id),
            "color": get_rarity_color(rarity_id),
        },
        "collections": collections,
        "team": {
            "id": team_id,
            "name": team_name,
        },
        "market_hash_name": translations.t(item.get("item_name"), use_default=True),
        "image": image,
        "model_player": item.get("model_player"),
        "original": {
            "name": item.get("name"),
            "image_inventory": image_key,
        },
    }


def generate_agents(state: State, translations: Translations) -> list[dict]:
    result = []
    for item in state.items.values():
        if item.get("prefab") != "customplayertradable":
            continue
        result.append(_parse_item(item, state, translations))
    return result

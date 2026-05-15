from api_gen.state import State
from api_gen.translations import Translations

# Tournament event IDs that have a Chinese-specific thumbnail variant
_CN_THUMBNAIL_EVENTS = {24}


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    folder = translations.language
    item_id: str = item["id"]
    parts = item_id.split("_")
    tournament = parts[0]
    highlight_type = parts[1] if len(parts) > 1 else ""

    keychain_name = translations.t(f"keychain_kc_{tournament}")
    highlight_name = translations.t(f"highlightreel_{tournament}_{highlight_type}")
    keychain_name_raw = translations.t(f"keychain_kc_{tournament}", use_default=True)
    highlight_name_raw = translations.t(
        f"highlightreel_{tournament}_{highlight_type}", use_default=True
    )
    charm_name = translations.t("CSGO_Tool_Keychain")

    name = translations.tc(
        "highlight_charm",
        {
            "charm_name": charm_name,
            "keychain_name": keychain_name,
            "highlight_name": highlight_name,
        },
    )

    description = translations.t(f"highlightdesc_{tournament}_{highlight_type}")

    tournament_event = (
        translations.t(f"csgo_watch_cat_tournament_{item['tournament_event_id']}")
        or translations.t(f"csgo_tournament_event_location_{item['tournament_event_id']}")
        or None
    )

    team0 = translations.t(f"csgo_teamid_{item['tournament_event_team0_id']}")
    team1 = translations.t(f"csgo_teamid_{item['tournament_event_team1_id']}")
    stage = translations.t(f"csgo_tournament_event_stage_{item['tournament_event_stage_id']}")

    market_hash_name = f"Souvenir Charm | {keychain_name_raw} | {highlight_name_raw}"

    image = state.cdn_images.get(item.get("image_inventory", "")) or item.get("image")

    # Video: replace _ww_ with _cn_ for Chinese locale
    video: str = item.get("video", "")
    if folder == "zh-CN":
        video = video.replace("_ww_", "_cn_")

    # Thumbnail: only Austin 2025 (event id 24) has a Chinese thumbnail variant
    thumbnail: str = item.get("thumbnail", "")
    if item.get("tournament_event_id") in _CN_THUMBNAIL_EVENTS and folder == "zh-CN":
        thumbnail = thumbnail.replace("/ww/", "/cn/")

    return {
        "id": f"highlight-{item['highlight_reel']}",
        "def_index": item["highlight_reel"],
        "name": name,
        "description": description,
        "tournament_event": tournament_event,
        "team0": team0,
        "team1": team1,
        "stage": stage,
        "tournament_player": item.get("tournament_player"),
        "map": item.get("tournament_event_map"),
        "market_hash_name": market_hash_name,
        "image": image,
        "video": video,
        "thumbnail": thumbnail,
        "original": {
            "id": item_id,
            "image_inventory": item.get("image_inventory"),
        },
    }


def generate_highlights(state: State, translations: Translations) -> list[dict]:
    result: list[dict] = []
    for item in state.highlight_reels:
        result.append(_parse_item(item, state, translations))
    return result

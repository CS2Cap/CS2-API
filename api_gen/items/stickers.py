from api_gen.constants import SPECIAL_NOTES, get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color

# object_ids that are not available in the game (DreamHack 2014 teams).
_EXCLUDED_OBJECT_IDS = {"232", "234", "235", "236"}


def _is_sticker(item: dict) -> bool:
    """Return True if *item* is a real sticker sticker kit."""
    if item.get("sticker_material") is None:
        return False

    # These team-roles capsule foil stickers are not available in the game.
    sticker_material = item["sticker_material"]
    if (
        sticker_material.startswith("team_roles_capsule")
        and sticker_material.endswith("_foil")
        and sticker_material != "team_roles_capsule/pro_foil"
    ):
        return False

    if str(item.get("object_id", "")) in _EXCLUDED_OBJECT_IDS:
        return False

    item_name = item.get("item_name", "")
    if "stickerkit_" not in item_name.lower():
        return False

    name = item.get("name", "")
    if "graffiti" in name:
        return False

    if "spray_" in name:
        return False

    return True


def _get_description(item: dict, translations: Translations) -> str:
    """Build the sticker description, optionally prepending tournament event text."""
    tournament_event_id = item.get("tournament_event_id")
    if tournament_event_id:
        event_name = translations.t(f"csgo_tournament_event_name_{tournament_event_id}") or ""
        event_desc_template = translations.t("csgo_event_desc") or "%s1"
        event_text = event_desc_template.replace("%s1", event_name)
        commemorates = f"<span style='color:#ffd700;'>{event_text}</span><br/><br/> "
    else:
        commemorates = ""

    msg = translations.t("CSGO_Tool_Sticker_Desc") or ""
    desc = translations.t(item.get("description_string"))
    description_string = item.get("description_string") or ""
    if desc and len(desc) > 0 and description_string != f"#{desc}":
        return f"{commemorates}{msg}<br><br>{desc}"
    return f"{commemorates}{msg}"


def _get_type(item: dict) -> str:
    """Categorize the sticker as Autograph, Team, Event, or Other."""
    if item.get("tournament_player_id"):
        return "Autograph"
    if item.get("tournament_team_id"):
        return "Team"
    if item.get("tournament_event_id"):
        return "Event"
    return "Other"


def _get_effect(item: dict, translations: Translations) -> str:
    """Determine the sticker effect by inspecting the English item name."""
    name_en = translations.t(item.get("item_name"), use_default=True) or ""

    if "(Holo)" in name_en or "(Holo, " in name_en:
        return "Holo"
    if "(Foil)" in name_en:
        return "Foil"
    if "(Lenticular)" in name_en:
        return "Lenticular"
    if "(Glitter)" in name_en or "(Glitter, " in name_en:
        return "Glitter"
    if "(Gold)" in name_en or "(Gold, " in name_en:
        return "Gold"
    if "(Embroidered)" in name_en or "(Embroidered, " in name_en:
        return "Embroidered"

    return "Other"


def _get_market_hash_name(item: dict, translations: Translations) -> str | None:
    """Return the Steam market hash name, or None if the sticker has no market listing."""
    tournament_event_id = item.get("tournament_event_id")
    sticker_material = item.get("sticker_material", "")

    # 1 - DreamHack 2013
    if tournament_event_id == 1:
        return None

    # 3 - Katowice 2014
    if tournament_event_id == 3:
        if (
            (_get_type(item) == "Event" and "gold_foil" in sticker_material)
            or (_get_effect(item, translations) == "Foil" and _get_type(item) == "Team")
        ):
            return None

    # 4 - Cologne 2014
    if tournament_event_id == 4:
        if _get_effect(item, translations) == "Foil" or sticker_material == "cologne2014/esl_c":
            return None

    # Events 5–16: legendary Gold stickers have no market listing
    # 5 - DreamHack 2014, 6 - Katowice 2015, 7 - Cologne 2015,
    # 8 - Cluj-Napoca 2015, 9 - Columbus 2016, 10 - Cologne 2016,
    # 11 - Atlanta 2017, 12 - Krakow 2017, 13 - Boston 2018,
    # 14 - London 2018, 15 - Katowice 2019, 16 - Berlin 2019
    if tournament_event_id in {5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}:
        if item.get("item_rarity") == "legendary" and _get_effect(item, translations) == "Gold":
            return None

    if sticker_material.startswith("tournament_assets/") or sticker_material.startswith("danger_zone/"):
        return None

    tool_name = translations.t("csgo_tool_sticker", use_default=True) or ""
    item_name = translations.t(item.get("item_name"), use_default=True) or ""
    return f"{tool_name} | {item_name}"


def _parse_item(item: dict, state: State, translations: Translations) -> dict:
    """Transform a raw sticker kit item into its API representation."""
    sticker_material = item.get("sticker_material", "").lower()
    image_key = f"econ/stickers/{sticker_material}"
    image = state.cdn_images.get(image_key) or get_image_url(image_key)

    # items_game.txt names it 'dignitas' but translations use 'teamdignitas'.
    if item.get("item_name") == "#StickerKit_dhw2014_dignitas_gold":
        item = dict(item)
        item["item_name"] = "#StickerKit_dhw2014_teamdignitas_gold"

    sticker_id = f"sticker-{item['object_id']}"

    item_rarity = item.get("item_rarity")
    if item_rarity:
        rarity_key = f"rarity_{item_rarity}"
    else:
        rarity_key = "rarity_default"

    tournament_event_id = item.get("tournament_event_id")
    tournament_team_id = item.get("tournament_team_id")
    tournament_player_id = item.get("tournament_player_id")

    # Tournament
    if tournament_event_id:
        tournament = {
            "id": tournament_event_id,
            "name": translations.t(f"csgo_tournament_event_nameshort_{tournament_event_id}"),
        }
    else:
        tournament = None

    # Team
    pro_team = state.pro_teams.get(tournament_team_id) if tournament_team_id else None
    if pro_team:
        team = {
            **pro_team,
            "name": translations.t(f"csgo_teamid_{tournament_team_id}"),
        }
    else:
        team = None

    # Player
    player = state.pro_players.get(tournament_player_id) if tournament_player_id else None

    # Crates
    crates_raw = state.crates_by_skins.get(sticker_id, [])
    crates = [
        {**c, "name": translations.t(c["name"])}
        for c in crates_raw
    ]

    # Collections
    collections_raw = state.collections_by_stickers.get(sticker_id, [])
    collections = [
        {**c, "name": translations.t(c["name"])}
        for c in collections_raw
    ]

    return {
        "id": sticker_id,
        "name": f"{translations.t('csgo_tool_sticker')} | {translations.t(item.get('item_name'))}",
        "description": _get_description(item, translations),
        "def_index": item["object_id"],
        "rarity": {
            "id": rarity_key,
            "name": translations.t(rarity_key),
            "color": get_rarity_color(rarity_key),
        },
        "special_notes": SPECIAL_NOTES.get(sticker_id),
        "crates": crates,
        "collections": collections,
        "type": _get_type(item),
        "market_hash_name": _get_market_hash_name(item, translations),
        "effect": _get_effect(item, translations),
        "tournament": tournament,
        "team": team,
        "player": player,
        "image": image,

        "original": {
            "name": item.get("name"),
            "image_inventory": image_key,
        },
    }


def generate_stickers(state: State, translations: Translations) -> list[dict]:
    return [
        _parse_item(item, state, translations)
        for item in state.sticker_kits
        if _is_sticker(item)
    ]

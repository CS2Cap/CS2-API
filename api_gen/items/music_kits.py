from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import get_rarity_color, is_exclusive

# Music kits that only exist in StatTrak form (no normal variant)
_KITS_ONLY_STATTRAK = {
    "beartooth_02",
    "blitzkids_01",
    "hundredth_01",
    "neckdeep_01",
    "roam_01",
    "twinatlantic_01",
    "skog_03",
}


def _get_description(item: dict, is_stattrak: bool, translations: Translations) -> str:
    if is_stattrak:
        stattrak_text = (
            f"<span style='color:#99ccff;'>{translations.t('attrib_killeater')}</span>"
            f"<br/><br/>"
            f"<span style='color:#cf6a32;'>{translations.t('killeaterdescriptionnotice_ocmvps')}</span>"
            f"<br/><br/>"
        )
    else:
        stattrak_text = ""

    return (
        f"{stattrak_text}"
        f"{translations.t('csgo_musickit_desc')}"
        f"<br/><br/>"
        f"{translations.t(item.get('loc_description'))}"
    )


def _parse_item(item: dict, state: State, translations: Translations) -> list[dict]:
    # Apply valve_02 alias before doing anything else
    if item.get("name") == "valve_02":
        item = dict(item)
        item["name"] = "valve_01"
        item["loc_name"] = "#musickit_valve_csgo_01"
        item["loc_description"] = "#musickit_valve_csgo_01_desc"

    image_key = item.get("image_inventory", "").lower()
    image = state.cdn_images.get(image_key) or get_image_url(image_key)

    exclusive = is_exclusive(item["name"])
    valve = item["name"] in {"valve_01", "valve_02", "valve_cs2_01"}

    rarity = {
        "id": "rarity_rare",
        "name": translations.t("rarity_rare"),
        "color": get_rarity_color("rarity_rare"),
    }

    coupon_name = item.get("coupon_name", "")
    original = {
        "name": item["name"],
        "image_inventory": image_key,
    }

    kits: list[dict] = []

    # Normal variant (skipped for kits_only_stattrak items)
    if item["name"] not in _KITS_ONLY_STATTRAK:
        if exclusive or valve:
            name = translations.t(item.get("loc_name"))
        else:
            name = translations.t(coupon_name)

        if exclusive or valve:
            market_hash_name = None
        else:
            kit_name = item["name"]
            market_hash_name = (
                f"Music Kit | {translations.t(f'musickit_{kit_name}', use_default=True)}"
            )

        kits.append({
            "id": f"music_kit-{item['object_id']}",
            "name": name,
            "description": _get_description(item, False, translations),
            "def_index": item["object_id"],
            "rarity": rarity,
            "market_hash_name": market_hash_name,
            "exclusive": exclusive,
            "image": image,
            "original": original,
        })

    # StatTrak variant (only if translation key exists)
    stattrak_name = translations.t(f"{coupon_name}_stattrak")
    if stattrak_name:
        if exclusive:
            st_market_hash_name = None
        else:
            kit_name = item["name"]
            st_market_hash_name = (
                f"StatTrak\u2122 Music Kit | "
                f"{translations.t(f'musickit_{kit_name}', use_default=True)}"
            )

        kits.append({
            "id": f"music_kit-{item['object_id']}_st",
            "name": stattrak_name,
            "description": _get_description(item, True, translations),
            "def_index": item["object_id"],
            "rarity": rarity,
            "market_hash_name": st_market_hash_name,
            "exclusive": False,
            "image": image,
            "original": original,
        })

    return kits


def generate_music_kits(state: State, translations: Translations) -> list[dict]:
    result: list[dict] = []
    for item in state.music_definitions:
        result.extend(_parse_item(item, state, translations))
    return result

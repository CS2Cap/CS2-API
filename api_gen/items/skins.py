from __future__ import annotations

import re

from api_gen.constants import SPECIAL_NOTES, get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import (
    KNIVES,
    WEAPON_ID_MAPPING,
    get_category,
    get_doppler_phase,
    get_rarity_color,
    get_weapon_name,
    get_wears,
    is_not_weapon,
)

_SKIN_RE = re.compile(r"econ/default_generated/(.*?)_light$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_pattern_name(weapon: str, string: str) -> str:
    """Strip the weapon prefix and return the pattern portion, lower-cased."""
    return string.replace(f"{weapon}_", "").lower()


def is_skin(icon_path: str) -> bool:
    """Return True if *icon_path* represents a paintable weapon skin icon."""
    if "newcs2" in icon_path:
        return False
    return bool(_SKIN_RE.search(icon_path.lower()))


def _get_skin_info(icon_path: str) -> tuple[str | bool, str]:
    """Extract (weapon, pattern) from a weapon-icon icon_path."""
    path = icon_path.lower()
    m = _SKIN_RE.search(path)
    skin_id = m.group(1)  # type: ignore[union-attr]
    weapon = get_weapon_name(skin_id)
    pattern = _get_pattern_name(weapon, skin_id)  # type: ignore[arg-type]
    return weapon, pattern


def _get_description(
    desc: str | None,
    paint_kits: dict,
    pattern: str,
    translations: Translations,
) -> str | None:
    """Build the skin description, appending paint-kit details when available."""
    # 1. Direct PaintKit translation
    pattern_desc = translations.t(f"#PaintKit_{pattern}")
    if pattern_desc and len(pattern_desc) > 0:
        return f"{desc} {pattern_desc}" if desc else pattern_desc

    pk = paint_kits.get(pattern) or {}
    description_tag = pk.get("description_tag")

    # 2. description_tag with _tag stripped
    if description_tag:
        tag_key = description_tag.lower().replace("_tag", "")
        tag_desc = translations.t(tag_key)
        if tag_desc and len(tag_desc) > 0:
            return f"{desc} {tag_desc}" if desc else tag_desc

        # 3. t_tag fallback on the raw description_tag
        idx_desc = translations.t_tag(description_tag)
        if idx_desc and len(idx_desc) > 0:
            return f"{desc} {idx_desc}" if desc else idx_desc

    return desc


def _parse_item(
    icon_path: str,
    object_id: str,
    state: State,
    translations: Translations,
) -> dict | None:
    """Build the full skin output dict for one weapon-icon entry.

    Parameters
    ----------
    icon_path: The icon path string from ``alternate_icons2.weapon_icons[key].icon_path``.
    object_id: The dict key from ``alternate_icons2.weapon_icons`` (used as the skin id).
    state: Populated State object.
    translations: Translations instance for the current language.
    """
    rarities = state.rarities
    paint_kits = state.paint_kits
    crates_by_skins = state.crates_by_skins
    souvenir_skins = state.souvenir_skins
    collections_by_skins = state.collections_by_skins
    cdn_images = state.cdn_images
    items = state.items

    weapon, pattern = _get_skin_info(icon_path)

    if not weapon:
        return None

    pk: dict = paint_kits.get(pattern) or {}

    doppler_phase = get_doppler_phase(pk.get("paint_index"))

    path_lower = icon_path.lower()
    image = (
        cdn_images.get(path_lower)
        or cdn_images.get(re.sub(r"_light$", "_medium", path_lower))
        or cdn_images.get(re.sub(r"_light$", "_heavy", path_lower))
        or get_image_url(path_lower)
    )

    # Translated weapon name and description
    item_data: dict = items.get(weapon) or {}
    if not is_not_weapon(weapon):
        translated_name = translations.t(item_data.get("item_name_prefab"))
        translated_description = translations.t(item_data.get("item_description_prefab"))
    else:
        translated_name = translations.t(item_data.get("item_name"))
        translated_description = translations.t(item_data.get("item_description"))

    # StatTrak eligibility
    is_stat_trak = (
        "knife" in weapon
        or "bayonet" in weapon
        or state.stattrak_skins.get(f"[{pattern}]{weapon}") is not None
    )

    # Knife vs glove distinction for rarity
    is_knife = "weapon_knife" in weapon or "weapon_bayonet" in weapon

    # Rarity resolution
    if not is_not_weapon(weapon):
        rarity_entry = rarities.get(f"[{pattern}]{weapon}") or {}
        rarity_raw = rarity_entry.get("rarity")
        rarity_id: str | None = f"rarity_{rarity_raw}_weapon" if rarity_raw else None
    else:
        # Knives → Covert, Gloves → Extraordinary
        rarity_id = "rarity_ancient_weapon" if is_knife else "rarity_ancient"

    # Team (CT, T, or both)
    used_by = item_data.get("used_by_classes") or {}
    if not used_by or len(used_by) == 2:
        team_id = "both"
    else:
        team_id = next(iter(used_by))

    if team_id == "both":
        team_name = translations.t("inv_filter_both_teams")
    elif team_id == "counter-terrorists":
        team_name = translations.t("inv_filter_ct")
    else:
        team_name = translations.t("inv_filter_t")

    # skin id
    skin_id = f"skin-{object_id}"

    # Souvenir flag
    is_souvenir: bool = souvenir_skins.get(skin_id, False)

    wear_min = float(pk.get("wear_remap_min", 0.0))
    wear_max = float(pk.get("wear_remap_max", 1.0))
    wear_keys = get_wears(wear_min, wear_max)
    wears = [{"id": wk, "name": translations.t(wk)} for wk in wear_keys]

    # Collections
    raw_collections = collections_by_skins.get(skin_id) or []
    collections = [
        {**c, "name": translations.t(c["name"])}
        for c in raw_collections
    ]

    # Crates
    raw_crates = crates_by_skins.get(skin_id) or []
    crates = [
        {**c, "name": translations.t(c["name"])}
        for c in raw_crates
    ]

    # Build pattern description tag
    pk_description_tag = pk.get("description_tag")
    pattern_name = translations.t(pk_description_tag)
    if pattern_name is not None:
        pattern_name = str(pattern_name)

    # Build item name
    if is_not_weapon(weapon):
        # Gloves / non-standard knives use tc("rare_special", ...)
        try:
            item_name = translations.tc(
                "rare_special",
                {
                    "item_name": translated_name or "",
                    "pattern": translations.t(pk_description_tag) or "",
                },
            )
        except (ValueError, KeyError):
            item_name = f"\u2605 {translated_name} | {translations.t(pk_description_tag)}"
    else:
        item_name = f"{translated_name} | {translations.t(pk_description_tag)}"

    result: dict = {
        "id": skin_id,
        "name": item_name,
        "description": _get_description(translated_description, paint_kits, pattern, translations),
        "weapon": {
            "id": weapon,
            "weapon_id": WEAPON_ID_MAPPING.get(weapon),
            "name": translated_name,
        },
        "category": {
            "id": get_category(weapon),
            "name": translations.t(get_category(weapon)),
        },
        "pattern": {
            "id": pattern,
            "name": pattern_name,
        },
        "min_float": wear_min,
        "max_float": wear_max,
        "rarity": {
            "id": rarity_id,
            "name": translations.t(rarity_id),
            "color": get_rarity_color(rarity_id),
        },
        "stattrak": is_stat_trak,
        "souvenir": is_souvenir,
        "paint_index": pk.get("paint_index"),
        "wears": wears,
        "collections": collections,
        "crates": crates,
        "special_notes": SPECIAL_NOTES.get(skin_id),
        "team": {
            "id": team_id,
            "name": team_name,
        },
        "legacy_model": pk.get("legacy_model"),
        "image": image,
        "original": {
            "name": item_data.get("name"),
        },
    }

    # Conditionally include doppler phase
    if doppler_phase is not None:
        result["phase"] = doppler_phase

    return result


def generate_skins(state: State, translations: Translations) -> list[dict]:
    """Return the full list of skins, including vanilla knives."""
    weapon_icons: dict = (
        state.items_game
        .get("alternate_icons2", {})
        .get("weapon_icons", {})
    )
    cdn_images = state.cdn_images
    crates_by_skins = state.crates_by_skins

    skins: list[dict] = []

    # Painted skins
    for key, item in weapon_icons.items():
        icon_path = item.get("icon_path", "")
        if not is_skin(icon_path):
            continue
        parsed = _parse_item(icon_path, key, state, translations)
        if parsed is not None:
            skins.append(parsed)

    # Vanilla knives
    for knife in KNIVES:
        knife_name = knife["name"]
        knife_item_name = knife["item_name"]
        knife_item_desc = knife["item_description"]

        image_key = f"econ/weapons/base_weapons/{knife_name}"
        image = cdn_images.get(image_key) or get_image_url(image_key)

        raw_crates = crates_by_skins.get(f"skin-vanilla-{knife_name}") or []
        crates = [
            {**c, "name": translations.t(c["name"])}
            for c in raw_crates
        ]

        try:
            vanilla_name = translations.tc(
                "rare_special_vanilla",
                {"item_name": translations.t(knife_item_name) or ""},
            )
        except (ValueError, KeyError):
            vanilla_name = f"\u2605 {translations.t(knife_item_name)}"

        skins.append({
            "id": f"skin-vanilla-{knife_name}",
            "name": vanilla_name,
            "description": translations.t(knife_item_desc),
            "weapon": {
                "id": knife_item_name,
                "weapon_id": WEAPON_ID_MAPPING.get(knife_name),
                "name": translations.t(knife_item_name),
            },
            "category": {
                "id": "sfui_invpanel_filter_melee",
                "name": translations.t("sfui_invpanel_filter_melee"),
            },
            "pattern": None,
            "min_float": None,
            "max_float": None,
            "rarity": {
                "id": "rarity_ancient_weapon",
                "name": translations.t("rarity_ancient_weapon"),
                "color": get_rarity_color("rarity_ancient_weapon"),
            },
            "stattrak": True,
            "paint_index": None,
            "crates": crates,
            "team": {
                "id": "both",
                "name": translations.t("inv_filter_both_teams"),
            },
            "legacy_model": True,
            "image": image,
            "original": {
                "name": knife_name,
            },
        })

    # Filter: name must not contain "null", rarity id must be truthy
    return [
        skin for skin in skins
        if skin.get("name") and "null" not in str(skin["name"])
        and skin.get("rarity", {}).get("id")
    ]

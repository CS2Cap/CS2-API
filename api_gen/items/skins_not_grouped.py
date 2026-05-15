from __future__ import annotations

from api_gen.constants import SPECIAL_NOTES, get_image_url

# Reusing helper from skins.py because fuck that
from api_gen.items.skins import _get_skin_info, is_skin
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import (
    KNIVES,
    WEAPON_ID_MAPPING,
    format_icon_path,
    get_category,
    get_doppler_phase,
    get_finish_style_link,
    get_rarity_color,
    get_wears,
    is_not_weapon,
    skin_market_hash_name,
)


# StatTrak description HTML prefix
def _stattrak_prefix(translations: Translations) -> str:
    """Return the HTML StatTrak prefix string prepended to descriptions."""
    killeater = translations.t("attrib_killeater") or ""
    killeater_desc = translations.t("killeaterdescriptionnotice_kills") or ""
    return (
        f"<span style='color:#99ccff;'>{killeater}</span>"
        f"<br/><br/>"
        f"<span style='color:#cf6a32;'>{killeater_desc}</span>"
        f"<br/><br/> "
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_description(
    desc: str | None,
    paint_kits: dict,
    pattern: str,
    translations: Translations,
    is_stattrak: bool,
) -> str | None:
    """Build the skin description, optionally prepending the StatTrak prefix."""
    prefix = _stattrak_prefix(translations) if is_stattrak else ""

    # 1. Direct PaintKit translation
    pattern_desc = translations.t(f"#PaintKit_{pattern}")
    if pattern_desc and len(pattern_desc) > 0:
        base = f"{desc} {pattern_desc}" if desc else pattern_desc
        return f"{prefix}{base}"

    pk = paint_kits.get(pattern) or {}
    description_tag = pk.get("description_tag")

    # 2. description_tag with _tag stripped
    if description_tag:
        tag_key = description_tag.lower().replace("_tag", "")
        tag_desc = translations.t(tag_key)
        if tag_desc and len(tag_desc) > 0:
            base = f"{desc} {tag_desc}" if desc else tag_desc
            return f"{prefix}{base}"

        # 3. t_tag fallback on the raw description_tag
        idx_desc = translations.t_tag(description_tag)
        if idx_desc and len(idx_desc) > 0:
            base = f"{desc} {idx_desc}" if desc else idx_desc
            return f"{prefix}{base}"

    return f"{prefix}{desc}" if (prefix and desc is not None) else desc


def _get_vanilla_description(
    desc: str | None,
    translations: Translations,
    is_stattrak: bool,
) -> str | None:
    """Build vanilla knife description, optionally prepending the StatTrak prefix."""
    prefix = _stattrak_prefix(translations) if is_stattrak else ""
    return f"{prefix}{desc}" if desc is not None else desc


# ---------------------------------------------------------------------------
# Core per-item expander
# ---------------------------------------------------------------------------

def _parse_item(
    icon_path: str,
    object_id: str,
    state: State,
    translations: Translations,
) -> list[dict]:
    """Expand one weapon-icon entry into a list of per-wear, per-variant dicts."""
    rarities = state.rarities
    paint_kits = state.paint_kits
    souvenir_skins = state.souvenir_skins
    cdn_images = state.cdn_images
    items = state.items

    weapon, pattern = _get_skin_info(icon_path)

    if not weapon:
        return []

    pk: dict = paint_kits.get(pattern) or {}

    item_data: dict = items.get(weapon) or {}

    # Translated weapon name and description
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

    # Souvenir eligibility
    skin_id = f"skin-{object_id}"
    is_souvenir: bool = souvenir_skins.get(skin_id, False)

    # Knife vs glove distinction for rarity
    is_knife = "weapon_knife" in weapon or "weapon_bayonet" in weapon

    # Rarity resolution
    if not is_not_weapon(weapon):
        rarity_entry = rarities.get(f"[{pattern}]{weapon}") or {}
        rarity_raw = rarity_entry.get("rarity")
        rarity_id: str | None = f"rarity_{rarity_raw}_weapon" if rarity_raw else None
    else:
        rarity_id = "rarity_ancient_weapon" if is_knife else "rarity_ancient"

    doppler_phase = get_doppler_phase(pk.get("paint_index"))

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

    wear_min = float(pk.get("wear_remap_min", 0.0))
    wear_max = float(pk.get("wear_remap_max", 1.0))
    wear_keys = get_wears(wear_min, wear_max)

    # Build the type list
    types: list[str] = [] if pattern == "hy_labrat_mp5" else ["skin"]
    if is_stat_trak:
        types.append("skin_stattrak")
    if is_souvenir:
        types.append("skin_souvenir")

    # Paint-kit description tag for names / market hash names
    pk_description_tag = pk.get("description_tag")
    pattern_name = translations.t(pk_description_tag)
    if pattern_name is not None:
        pattern_name = str(pattern_name)

    icon_path_lower = icon_path.lower()

    results: list[dict] = []

    for variant_type in types:
        is_st = variant_type == "skin_stattrak"
        is_so = variant_type == "skin_souvenir"

        for index, wear_key in enumerate(wear_keys):
            wear_name = translations.t(wear_key)

            # Build variant name via tc()
            if is_not_weapon(weapon):
                tc_key = (
                    "rare_special_with_wear_stattrak" if is_st else "rare_special_with_wear"
                )
                try:
                    item_name = translations.tc(
                        tc_key,
                        {
                            "item_name": translated_name or "",
                            "pattern": translations.t(pk_description_tag) or "",
                            "wear": wear_name or "",
                        },
                    )
                except (ValueError, KeyError):
                    star = "\u2605"
                    st_prefix = "StatTrak\u2122 " if is_st else ""
                    item_name = (
                        f"{star} {st_prefix}{translated_name} | "
                        f"{translations.t(pk_description_tag)} ({wear_name})"
                    )
            else:
                try:
                    item_name = translations.tc(
                        variant_type,
                        {
                            "item_name": translated_name or "",
                            "pattern": translations.t(pk_description_tag) or "",
                            "wear": wear_name or "",
                        },
                    )
                except (ValueError, KeyError):
                    if is_st:
                        item_name = (
                            f"StatTrak\u2122 {translated_name} | "
                            f"{translations.t(pk_description_tag)} ({wear_name})"
                        )
                    elif is_so:
                        item_name = (
                            f"Souvenir {translated_name} | "
                            f"{translations.t(pk_description_tag)} ({wear_name})"
                        )
                    else:
                        item_name = (
                            f"{translated_name} | "
                            f"{translations.t(pk_description_tag)} ({wear_name})"
                        )

            # Wear-specific icon path and image
            wear_icon_path = format_icon_path(icon_path_lower, wear_key)
            image = (
                cdn_images.get(wear_icon_path)
                or get_image_url(wear_icon_path)
            )

            # Variant ID suffix
            if is_st:
                id_suffix = "_st"
            elif is_so:
                id_suffix = "_so"
            else:
                id_suffix = ""

            entry: dict = {
                "id": f"{skin_id}_{index}{id_suffix}",
                "skin_id": skin_id,
                "name": item_name,
                "description": _get_description(
                    translated_description, paint_kits, pattern, translations, is_st
                ),
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
                "wear": {
                    "id": wear_key,
                    "name": wear_name,
                },
                "stattrak": is_st,
                "souvenir": is_so,
                "paint_index": pk.get("paint_index"),
                "rarity": {
                    "id": rarity_id,
                    "name": translations.t(rarity_id),
                    "color": get_rarity_color(rarity_id),
                },
                "special_notes": SPECIAL_NOTES.get(skin_id),
                "team": {
                    "id": team_id,
                    "name": team_name,
                },
                "style": {
                    "id": pk.get("style_id"),
                    "name": translations.t(pk.get("style_name")),
                    "url": get_finish_style_link(pk.get("style_id")),
                },
                "legacy_model": pk.get("legacy_model"),
                "market_hash_name": skin_market_hash_name(
                    item_name=translations.t(
                        item_data.get("item_name_prefab")
                        if not is_not_weapon(weapon)
                        else item_data.get("item_name"),
                        use_default=True,
                    ),
                    pattern=translations.t(pk_description_tag, use_default=True),
                    wear=translations.t(wear_key, use_default=True),
                    is_stattrak=is_st,
                    is_souvenir=is_so,
                    is_weapon=not is_not_weapon(weapon),
                    is_vanilla=False,
                ),
                "image": image,
                "original": {
                    "name": item_data.get("name"),
                    "image_inventory": wear_icon_path,
                },
            }

            if doppler_phase is not None:
                entry["phase"] = doppler_phase

            results.append(entry)

    return results


def generate_skins_not_grouped(state: State, translations: Translations) -> list[dict]:
    """Return the full flat list of per-wear skin variants, including vanilla knives."""
    weapon_icons: dict = (
        state.items_game
        .get("alternate_icons2", {})
        .get("weapon_icons", {})
    )
    cdn_images = state.cdn_images

    skins: list[dict] = []

    # Painted skins
    for key, item in weapon_icons.items():
        icon_path = item.get("icon_path", "")
        if not is_skin(icon_path):
            continue
        expanded = _parse_item(icon_path, key, state, translations)
        skins.extend(expanded)

    # Vanilla knives
    vanilla_types = ["rare_special_vanilla", "rare_special_vanilla_stattrak"]

    for variant_type in vanilla_types:
        is_st = variant_type == "rare_special_vanilla_stattrak"

        for knife in KNIVES:
            knife_name = knife["name"]
            knife_item_name = knife["item_name"]
            knife_item_desc = knife["item_description"]

            translated_knife_name = translations.t(knife_item_name)
            translated_knife_desc = translations.t(knife_item_desc)

            image_key = f"econ/weapons/base_weapons/{knife_name}"
            image = cdn_images.get(image_key) or get_image_url(image_key)

            try:
                item_name = translations.tc(
                    variant_type,
                    {"item_name": translated_knife_name or ""},
                )
            except (ValueError, KeyError):
                star = "\u2605"
                st_prefix = "StatTrak\u2122 " if is_st else ""
                item_name = f"{star} {st_prefix}{translated_knife_name}"

            entry: dict = {
                "id": (
                    f"skin-vanilla-{knife_name}_st"
                    if is_st
                    else f"skin-vanilla-{knife_name}"
                ),
                "skin_id": f"skin-vanilla-{knife_name}",
                "name": item_name,
                "description": _get_vanilla_description(
                    translated_knife_desc, translations, is_st
                ),
                "weapon": {
                    "id": knife_item_name,
                    "weapon_id": WEAPON_ID_MAPPING.get(knife_name),
                    "name": translated_knife_name,
                },
                "category": {
                    "id": "sfui_invpanel_filter_melee",
                    "name": translations.t("sfui_invpanel_filter_melee"),
                },
                "rarity": {
                    "id": "rarity_ancient_weapon",
                    "name": translations.t("rarity_ancient_weapon"),
                    "color": get_rarity_color("rarity_ancient_weapon"),
                },
                "stattrak": is_st,
                "paint_index": None,
                "market_hash_name": skin_market_hash_name(
                    item_name=translations.t(knife_item_name, use_default=True),
                    pattern=None,
                    wear=None,
                    is_stattrak=is_st,
                    is_souvenir=False,
                    is_weapon=False,
                    is_vanilla=True,
                ),
                "team": {
                    "id": "both",
                    "name": translations.t("inv_filter_both_teams"),
                },
                "style": {
                    "id": 0,
                    "name": translations.t("SFUI_ItemInfo_FinishStyle_0"),
                    "url": get_finish_style_link(0),
                },
                "legacy_model": True,
                "image": image,
                "original": {
                    "name": knife_name,
                    "image_inventory": image_key,
                },
            }

            skins.append(entry)

    # Filter: name must not contain "null", rarity id must be truthy
    return [
        skin for skin in skins
        if skin.get("name") and "null" not in str(skin["name"])
        and skin.get("rarity", {}).get("id")
    ]

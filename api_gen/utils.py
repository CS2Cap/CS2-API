"""
Utility functions and data tables ported from CSGO-API/utils/index.js.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Data tables
# ---------------------------------------------------------------------------

WEAPON_NAMES = [
    "weapon_taser",
    "weapon_deagle",
    "weapon_elite",
    "weapon_fiveseven",
    "weapon_glock",
    "weapon_ak47",
    "weapon_aug",
    "weapon_awp",
    "weapon_famas",
    "weapon_g3sg1",
    "weapon_galilar",
    "weapon_m249",
    "weapon_mac10",
    "weapon_p90",
    "weapon_mp5sd",
    "weapon_ump45",
    "weapon_xm1014",
    "weapon_bizon",
    "weapon_mag7",
    "weapon_negev",
    "weapon_sawedoff",
    "weapon_tec9",
    "weapon_hkp2000",
    "weapon_mp7",
    "weapon_mp9",
    "weapon_nova",
    "weapon_p250",
    "weapon_scar20",
    "weapon_sg556",
    "weapon_ssg08",
    "weapon_m4a1_silencer",
    "weapon_m4a1",
    "weapon_usp_silencer",
    "weapon_cz75a",
    "weapon_revolver",
    "weapon_bayonet",
    "weapon_knife_css",
    "weapon_knife_flip",
    "weapon_knife_gut",
    "weapon_knife_karambit",
    "weapon_knife_m9_bayonet",
    "weapon_knife_tactical",
    "weapon_knife_falchion",
    "weapon_knife_survival_bowie",
    "weapon_knife_butterfly",
    "weapon_knife_push",
    "weapon_knife_cord",
    "weapon_knife_canis",
    "weapon_knife_ursus",
    "weapon_knife_gypsy_jackknife",
    "weapon_knife_outdoor",
    "weapon_knife_stiletto",
    "weapon_knife_widowmaker",
    "weapon_knife_skeleton",
    "weapon_knife_kukri",
    "studded_bloodhound_gloves",
    "studded_brokenfang_gloves",
    "sporty_gloves",
    "slick_gloves",
    "leather_handwraps",
    "motorcycle_gloves",
    "specialist_gloves",
    "studded_hydra_gloves",
]

WEAPON_ID_MAPPING = {
    "weapon_taser": 31,
    "weapon_deagle": 1,
    "weapon_elite": 2,
    "weapon_fiveseven": 3,
    "weapon_glock": 4,
    "weapon_ak47": 7,
    "weapon_aug": 8,
    "weapon_awp": 9,
    "weapon_famas": 10,
    "weapon_g3sg1": 11,
    "weapon_galilar": 13,
    "weapon_m249": 14,
    "weapon_mac10": 17,
    "weapon_p90": 19,
    "weapon_mp5sd": 23,
    "weapon_ump45": 24,
    "weapon_xm1014": 25,
    "weapon_bizon": 26,
    "weapon_mag7": 27,
    "weapon_negev": 28,
    "weapon_sawedoff": 29,
    "weapon_tec9": 30,
    "weapon_hkp2000": 32,
    "weapon_mp7": 33,
    "weapon_mp9": 34,
    "weapon_nova": 35,
    "weapon_p250": 36,
    "weapon_scar20": 38,
    "weapon_sg556": 39,
    "weapon_ssg08": 40,
    "weapon_m4a1_silencer": 60,
    "weapon_m4a1": 16,
    "weapon_usp_silencer": 61,
    "weapon_cz75a": 63,
    "weapon_revolver": 64,
    "weapon_bayonet": 500,
    "weapon_knife_css": 503,
    "weapon_knife_flip": 505,
    "weapon_knife_gut": 506,
    "weapon_knife_karambit": 507,
    "weapon_knife_m9_bayonet": 508,
    "weapon_knife_tactical": 509,
    "weapon_knife_falchion": 512,
    "weapon_knife_survival_bowie": 514,
    "weapon_knife_butterfly": 515,
    "weapon_knife_push": 516,
    "weapon_knife_cord": 517,
    "weapon_knife_canis": 518,
    "weapon_knife_ursus": 519,
    "weapon_knife_gypsy_jackknife": 520,
    "weapon_knife_outdoor": 521,
    "weapon_knife_stiletto": 522,
    "weapon_knife_widowmaker": 523,
    "weapon_knife_skeleton": 525,
    "weapon_knife_kukri": 526,
    "studded_bloodhound_gloves": 5027,
    "studded_brokenfang_gloves": 4725,
    "sporty_gloves": 5030,
    "slick_gloves": 5031,
    "leather_handwraps": 5032,
    "motorcycle_gloves": 5033,
    "specialist_gloves": 5034,
    "studded_hydra_gloves": 5035,
    "weapon_flashbang": 43,
    "weapon_hegrenade": 44,
    "weapon_smokegrenade": 45,
    "weapon_molotov": 46,
    "weapon_decoy": 47,
    "weapon_incgrenade": 48,
    "weapon_c4": 49,
    "weapon_healthshot": 57,
    "weapon_knife_t": 59,
    "weapon_knife": 42,
    "t_gloves": 5028,
    "ct_gloves": 5029,
}

KNIVES = [
    {
        "name": "weapon_bayonet",
        "item_name": "sfui_wpnhud_knifebayonet",
        "item_description": "csgo_item_desc_knife_bayonet",
    },
    {
        "name": "weapon_knife_css",
        "item_name": "sfui_wpnhud_knifecss",
        "item_description": "csgo_item_desc_knife_css",
    },
    {
        "name": "weapon_knife_flip",
        "item_name": "sfui_wpnhud_knifeflip",
        "item_description": "csgo_item_desc_knife_flip",
    },
    {
        "name": "weapon_knife_gut",
        "item_name": "sfui_wpnhud_knifegut",
        "item_description": "csgo_item_desc_knife_gut",
    },
    {
        "name": "weapon_knife_karambit",
        "item_name": "sfui_wpnhud_knifekaram",
        "item_description": "csgo_item_desc_knife_karam",
    },
    {
        "name": "weapon_knife_m9_bayonet",
        "item_name": "sfui_wpnhud_knifem9",
        "item_description": "csgo_item_desc_knifem9",
    },
    {
        "name": "weapon_knife_tactical",
        "item_name": "sfui_wpnhud_knifetactical",
        "item_description": "csgo_item_desc_knifetactical",
    },
    {
        "name": "weapon_knife_falchion",
        "item_name": "sfui_wpnhud_knife_falchion_advanced",
        "item_description": "csgo_item_desc_knife_falchion_advanced",
    },
    {
        "name": "weapon_knife_survival_bowie",
        "item_name": "sfui_wpnhud_knife_survival_bowie",
        "item_description": "csgo_item_desc_knife_survival_bowie",
    },
    {
        "name": "weapon_knife_butterfly",
        "item_name": "sfui_wpnhud_knife_butterfly",
        "item_description": "csgo_item_desc_knife_butterfly",
    },
    {
        "name": "weapon_knife_push",
        "item_name": "sfui_wpnhud_knife_push",
        "item_description": "csgo_item_desc_knife_push",
    },
    {
        "name": "weapon_knife_cord",
        "item_name": "sfui_wpnhud_knife_cord",
        "item_description": "csgo_item_desc_knife_cord",
    },
    {
        "name": "weapon_knife_canis",
        "item_name": "sfui_wpnhud_knife_canis",
        "item_description": "csgo_item_desc_knife_canis",
    },
    {
        "name": "weapon_knife_ursus",
        "item_name": "sfui_wpnhud_knife_ursus",
        "item_description": "csgo_item_desc_knife_ursus",
    },
    {
        "name": "weapon_knife_gypsy_jackknife",
        "item_name": "sfui_wpnhud_knife_gypsy_jackknife",
        "item_description": "csgo_item_desc_knife_gypsy_jackknife",
    },
    {
        "name": "weapon_knife_outdoor",
        "item_name": "sfui_wpnhud_knife_outdoor",
        "item_description": "csgo_item_desc_knife_outdoor",
    },
    {
        "name": "weapon_knife_stiletto",
        "item_name": "sfui_wpnhud_knife_stiletto",
        "item_description": "csgo_item_desc_knife_stiletto",
    },
    {
        "name": "weapon_knife_widowmaker",
        "item_name": "sfui_wpnhud_knife_widowmaker",
        "item_description": "csgo_item_desc_knife_widowmaker",
    },
    {
        "name": "weapon_knife_skeleton",
        "item_name": "sfui_wpnhud_knife_skeleton",
        "item_description": "csgo_item_desc_knife_skeleton",
    },
    {
        "name": "weapon_knife_kukri",
        "item_name": "sfui_wpnhud_knife_kukri",
        "item_description": "csgo_item_desc_knife_kukri",
    },
]

DOPPLER_PHASES = {
    # Doppler
    415: "Ruby",
    416: "Sapphire",
    417: "Black Pearl",
    418: "Phase 1",
    419: "Phase 2",
    420: "Phase 3",
    421: "Phase 4",
    # Gamma Doppler
    568: "Emerald",
    569: "Phase 1",
    570: "Phase 2",
    571: "Phase 3",
    572: "Phase 4",
    # Doppler (Butterfly Knife, Shadow Daggers)
    617: "Black Pearl",
    618: "Phase 2",
    619: "Sapphire",
    # Doppler (Talon Knife)
    852: "Phase 1",
    853: "Phase 2",
    854: "Phase 3",
    855: "Phase 4",
    # Gamma Doppler (Glock-18)
    1119: "Emerald",
    1120: "Phase 1",
    1121: "Phase 2",
    1122: "Phase 3",
    1123: "Phase 4",
}

GRAFFITI_VARIATIONS: dict[str, list[int]] = {
    "spray_std_axes_crossed": [0],
    "spray_std_bubble_dead": [0],
    "spray_std_chess_king": [0],
    "spray_std_crown": [0],
    "spray_std_dollar": [7, 8, 9, 10],
    "spray_std_double_kill": [0],
    "spray_std_eco_pistol": [0],
    "spray_std_emo_angry": [0],
    "spray_std_emo_brainless": [0],
    "spray_std_emo_despair": [0],
    "spray_std_emo_happy": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18],
    "spray_std_emo_ninja": [0],
    "spray_std_emo_worry": [0],
    "spray_std_evil_eye": [0],
    "spray_std_eyeball": [0],
    "spray_std_gg_01": [0],
    "spray_std_gg_02": [0],
    "spray_std_glhf": [0],
    "spray_std_gunsmoke": [0],
    "spray_std_hand_butterfly": [0],
    "spray_std_hand_loser": [0],
    "spray_std_hat_sherif": [0],
    "spray_std_headstone_rip": [0],
    "spray_std_heart": [1, 2, 3, 4, 5, 6, 15, 16, 17, 18],
    "spray_std_hl_eightball": [0],
    "spray_std_hl_lambda": [0],
    "spray_std_hl_smiley": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18],
    "spray_std_jump_shot": [0],
    "spray_std_karambit": [0],
    "spray_std_knives_crossed": [0],
    "spray_std_moly": [1, 2, 3, 4, 5, 6, 15, 16, 17, 18],
    "spray_std_necklace_dollar": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 18, 19],
    "spray_std_no_scope": [0],
    "spray_std_piggles": [1, 2, 3, 4, 5, 6, 15, 16, 17, 18],
    "spray_std_popdog": [0],
    "spray_std_rooster": [0],
    "spray_std_salty": [19],
    "spray_std_sorry": [0],
    "spray_std_tongue": [0],
    "spray_std_wings": [0],
    "spray_std_gtg": [0],
    # selfopeningitem_crate_spray_std2_1
    "spray_std2_applause": [0],
    "spray_std2_beep": [0],
    "spray_std2_boom": [0],
    "spray_std2_brightstar": [0],
    "spray_std2_brokenheart": [0],
    "spray_std2_chef_kiss": [0],
    "spray_std2_chick": [0],
    "spray_std2_chunkychicken": [0],
    "spray_std2_goofy": [0],
    "spray_std2_grimace": [0],
    "spray_std2_happy_cat": [0],
    "spray_std2_hop": [0],
    "spray_std2_kiss": [0],
    "spray_std2_lightbulb": [6, 19],
    "spray_std2_little_crown": [0],
    "spray_std2_omg": [0],
    "spray_std2_silverbullet": [0],
    "spray_std2_smirk": [0],
    "spray_std2_thoughtfull": [0],
    # selfopeningitem_crate_spray_std2_2
    "spray_std2_1g": [0],
    "spray_std2_200iq": [0],
    "spray_std2_bubble_denied": [0],
    "spray_std2_bubble_question": [0],
    "spray_std2_choke": [0],
    "spray_std2_dead_now": [0],
    "spray_std2_fart": [0],
    "spray_std2_little_ez": [0],
    "spray_std2_littlebirds": [0],
    "spray_std2_nt": [0],
    "spray_std2_okay": [0],
    "spray_std2_oops": [0],
    "spray_std2_puke": [0],
    "spray_std2_rly": [0],
    "spray_std2_smarm": [0],
    "spray_std2_smooch": [0],
    "spray_std2_uhoh": [0],
    # selfopeningitem_crate_spray_std3
    "spray_std3_ak47": [0],
    "spray_std3_aug": [0],
    "spray_std3_awp": [0],
    "spray_std3_bizon": [0],
    "spray_std3_cz": [0],
    "spray_std3_famas": [0],
    "spray_std3_galil": [0],
    "spray_std3_m4a1": [0],
    "spray_std3_m4a4": [0],
    "spray_std3_mac10": [0],
    "spray_std3_mp7": [0],
    "spray_std3_mp9": [0],
    "spray_std3_p90": [0],
    "spray_std3_sg553": [0],
    "spray_std3_ump": [0],
    "spray_std3_xm1014": [0],
}

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def get_weapon_name(string: str) -> str | bool:
    """Find which weapon identifier *string* contains and return it, or False."""
    for weapon in WEAPON_NAMES:
        if weapon in string:
            return weapon
    return False


def is_not_weapon(string: str) -> bool:
    """Return True if the string represents a knife, bayonet, or non-weapon (gloves, etc.)."""
    return (
        "weapon_" not in string
        or "weapon_knife" in string
        or "weapon_bayonet" in string
    )


def get_category(weapon: str) -> str | None:
    """Map a weapon identifier to its inventory category translation key."""
    pistols = {
        "weapon_deagle", "weapon_elite", "weapon_fiveseven", "weapon_glock",
        "weapon_tec9", "weapon_hkp2000", "weapon_p250", "weapon_usp_silencer",
        "weapon_cz75a", "weapon_revolver",
    }
    rifles = {
        "weapon_ak47", "weapon_aug", "weapon_awp", "weapon_famas", "weapon_g3sg1",
        "weapon_galilar", "weapon_scar20", "weapon_sg556", "weapon_ssg08",
        "weapon_m4a1_silencer", "weapon_m4a1",
    }
    heavy = {
        "weapon_m249", "weapon_xm1014", "weapon_mag7", "weapon_negev",
        "weapon_sawedoff", "weapon_nova",
    }
    smgs = {
        "weapon_mac10", "weapon_p90", "weapon_mp5sd", "weapon_ump45",
        "weapon_bizon", "weapon_mp7", "weapon_mp9",
    }
    melee = {
        "weapon_bayonet", "weapon_knife_css", "weapon_knife_flip", "weapon_knife_gut",
        "weapon_knife_karambit", "weapon_knife_m9_bayonet", "weapon_knife_tactical",
        "weapon_knife_falchion", "weapon_knife_survival_bowie", "weapon_knife_butterfly",
        "weapon_knife_push", "weapon_knife_cord", "weapon_knife_canis", "weapon_knife_ursus",
        "weapon_knife_gypsy_jackknife", "weapon_knife_outdoor", "weapon_knife_stiletto",
        "weapon_knife_widowmaker", "weapon_knife_skeleton", "weapon_knife_kukri",
        "weapon_knife", "weapon_knife_t",
    }
    gloves = {
        "studded_bloodhound_gloves", "studded_brokenfang_gloves", "sporty_gloves",
        "slick_gloves", "leather_handwraps", "motorcycle_gloves", "specialist_gloves",
        "studded_hydra_gloves", "ct_gloves", "t_gloves",
    }
    equipment = {"weapon_taser", "weapon_healthshot"}
    grenades = {
        "weapon_flashbang", "weapon_hegrenade", "weapon_smokegrenade",
        "weapon_molotov", "weapon_decoy", "weapon_incgrenade",
    }

    if weapon in pistols:
        return "csgo_inventory_weapon_category_pistols"
    if weapon in rifles:
        return "csgo_inventory_weapon_category_rifles"
    if weapon in heavy:
        return "csgo_inventory_weapon_category_heavy"
    if weapon in smgs:
        return "csgo_inventory_weapon_category_smgs"
    if weapon in melee:
        return "sfui_invpanel_filter_melee"
    if weapon in gloves:
        return "sfui_invpanel_filter_gloves"
    if weapon in equipment:
        return "loadoutslot_equipment"
    if weapon in grenades:
        return "loadoutslot_grenade"
    if weapon == "weapon_c4":
        return "loadoutslot_c4"
    return None


def get_wears(min_float: float, max_float: float) -> list[str]:
    """Return the list of wear level keys supported by the given float range."""
    wears = [
        {"wear": "SFUI_InvTooltip_Wear_Amount_0", "min": 0.0,  "max": 0.07},
        {"wear": "SFUI_InvTooltip_Wear_Amount_1", "min": 0.07, "max": 0.15},
        {"wear": "SFUI_InvTooltip_Wear_Amount_2", "min": 0.15, "max": 0.38},
        {"wear": "SFUI_InvTooltip_Wear_Amount_3", "min": 0.38, "max": 0.45},
        {"wear": "SFUI_InvTooltip_Wear_Amount_4", "min": 0.45, "max": 1.0},
    ]
    return [
        r["wear"] for r in wears
        if r["max"] > min_float and r["min"] < max_float
    ]


def get_doppler_phase(paint_index: int) -> str | None:
    """Return the Doppler phase name for *paint_index*, or None if not found."""
    return DOPPLER_PHASES.get(paint_index)


def get_rarity_color(rarity_id: str | None) -> str | None:
    """Return the hex colour string for a rarity identifier, or None."""
    if rarity_id is None:
        return None
    rarity_id = rarity_id.lower()
    mapping = {
        "rarity_default": "#ded6cc",
        "rarity_legendary_character": "#d32ce6",
        "rarity_legendary_weapon": "#d32ce6",
        "rarity_legendary": "#d32ce6",
        "rarity_ancient_character": "#eb4b4b",
        "rarity_ancient_weapon": "#eb4b4b",
        "rarity_ancient": "#eb4b4b",
        "rarity_mythical_character": "#8847ff",
        "rarity_mythical_weapon": "#8847ff",
        "rarity_mythical": "#8847ff",
        "rarity_rare_character": "#4b69ff",
        "rarity_rare_weapon": "#4b69ff",
        "rarity_rare": "#4b69ff",
        "rarity_common_weapon": "#b0c3d9",
        "rarity_common": "#b0c3d9",
        "rarity_uncommon_weapon": "#5e98d9",
        "rarity_contraband": "#e4ae39",
        "rarity_contraband_weapon": "#e4ae39",
    }
    return mapping.get(rarity_id)


def is_exclusive(name: str) -> bool:
    """Return True if *name* is an exclusive music kit identifier."""
    return name in {"halo_01", "hlalyx_01", "hades_01"}


def get_graffiti_variations(material: str) -> list[int]:
    """Return the list of colour variation indices for a graffiti material."""
    return GRAFFITI_VARIATIONS.get(material, [])


def get_player_name_of_highlight(id: str, players: dict) -> str:
    """Resolve a highlight ID to a player name, applying known typo corrections."""
    id = id.split("_")[1]

    if id.startswith("shiro"):
        id = id.replace("shiro", "sh1ro", 1)
    if id.startswith("magix"):
        id = id.replace("magix", "magixx", 1)
    if id.startswith("torszi"):
        id = id.replace("torszi", "torzsi", 1)
    if id.startswith("zontix"):
        id = id.replace("zontix", "zont1x", 1)
    if id.startswith("techno"):
        id = id.replace("techno", "techno4k", 1)
    if id.startswith("tehcno"):
        id = id.replace("tehcno", "techno4k", 1)
    if id.startswith("wonderful"):
        id = id.replace("wonderful", "w0nderful", 1)
    if id.startswith("yuuri"):
        id = id.replace("yuuri", "yuurih", 1)
    if id.startswith("flames"):
        id = id.replace("flames", "flamez", 1)
    if id.startswith("mezi"):
        id = id.replace("mezi", "mezii", 1)
    if id.startswith("senznu"):
        id = id.replace("senznu", "senzu", 1)
    if id.startswith("jimphat"):
        id = id.replace("jimphat", "jimpphat", 1)

    if id == "mongolzscaredofs1mplevsfazeonanubis":
        id = "s1mple"
    if id == "boosttorszitoentryvsspiritonnuke":
        id = "torzsi"

    import re
    if id.startswith("qf-") or id.startswith("sf-") or id.startswith("gf-"):
        id = re.sub(r"^(qf|sf|gf)-", "", id)

    for name in players.values():
        if id.startswith(name.lower()):
            return name
    return "Unknown Player"


def get_collectible_rarity(prefab: str) -> str | None:
    """Map a collectible prefab string to its rarity key."""
    keys = prefab.split(" ")
    for key in keys:
        if key.endswith("_tournament_pass_prefab"):
            return "rarity_common"
        if key.endswith("_tournament_journal_prefab"):
            return "rarity_ancient"
        ancient_keys = {
            "collectible_untradable_coin", "majors_trophy", "map_token",
            "pickem_trophy", "prestige_coin", "season1_coin", "season10_coin",
            "season11_coin", "season2_coin", "season3_coin", "season4_coin",
            "season5_coin", "season6_coin", "season7_coin", "season8_coin",
            "season9_coin", "premier_season_coin",
        }
        if key in {"season_pass", "season_tiers"}:
            return "rarity_common"
        if key in ancient_keys:
            return "rarity_ancient"
    return None


def skin_market_hash_name(
    *,
    item_name: str,
    pattern: str,
    wear: str,
    is_stattrak: bool,
    is_souvenir: bool,
    is_weapon: bool,
    is_vanilla: bool,
) -> str:
    """Generate the Steam market hash name string for a skin."""
    if is_weapon:
        if is_stattrak:
            return f"StatTrak\u2122 {item_name} | {pattern} ({wear})"
        if is_souvenir:
            return f"Souvenir {item_name} | {pattern} ({wear})"
        return f"{item_name} | {pattern} ({wear})"
    else:
        if is_vanilla:
            if is_stattrak:
                return f"\u2605 StatTrak\u2122 {item_name}"
            return f"\u2605 {item_name}"
        else:
            if is_stattrak:
                return f"\u2605 StatTrak\u2122 {item_name} | {pattern} ({wear})"
            return f"\u2605 {item_name} | {pattern} ({wear})"


def filter_unique_by_attribute(items: list[dict], attr: str) -> list[dict]:
    """Return *items* deduplicated by *attr*, preserving first occurrence order."""
    seen: set[Any] = set()
    result = []
    for item in items:
        val = item[attr]
        if val not in seen:
            seen.add(val)
            result.append(item)
    return result


def format_icon_path(icon_path: str, wear: str) -> str:
    """Map a wear level key to the appropriate icon path variant suffix."""
    import re
    if wear in ("SFUI_InvTooltip_Wear_Amount_2", "SFUI_InvTooltip_Wear_Amount_3"):
        icon_path = re.sub(r"_light$", "_medium", icon_path)
    if wear in ("SFUI_InvTooltip_Wear_Amount_4",):
        icon_path = re.sub(r"_light$", "_heavy", icon_path)
    return icon_path


def get_finish_style_link(style_id: int) -> str | None:
    """Map a finish style ID to its counter-strike.net workshop URL."""
    mapping = {
        1:  "https://www.counter-strike.net/workshop/workshopfinishes#solidcolorstyle",
        2:  "https://www.counter-strike.net/workshop/workshopfinishes#hydrographic",
        3:  "https://www.counter-strike.net/workshop/workshopfinishes#spraypaint",
        4:  "https://www.counter-strike.net/workshop/workshopfinishes#anodized",
        5:  "https://www.counter-strike.net/workshop/workshopfinishes#anodizedmulticolored",
        6:  "https://www.counter-strike.net/workshop/workshopfinishes#anodizedairbrushed",
        7:  "https://www.counter-strike.net/workshop/workshopfinishes#custompaint",
        8:  "https://www.counter-strike.net/workshop/workshopfinishes#patina",
        9:  "https://www.counter-strike.net/workshop/workshopfinishes#gunsmith",
        10: "https://www.counter-strike.net/workshop/workshopfinishes#patina",
    }
    return mapping.get(style_id)

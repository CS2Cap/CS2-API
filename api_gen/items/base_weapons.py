from __future__ import annotations

from api_gen.constants import get_image_url
from api_gen.state import State
from api_gen.translations import Translations
from api_gen.utils import WEAPON_ID_MAPPING, get_category

_BASE_WEAPON_SPECS: list[tuple[str, str, str]] = [
    ("ct_gloves",                   "csgo_wearable_ct_defaultgloves",           "csgo_wearable_ct_defaultgloves_desc"),
    ("t_gloves",                    "csgo_wearable_t_defaultgloves",            "csgo_wearable_t_defaultgloves_desc"),
    ("weapon_ak47",                 "sfui_wpnhud_ak47",                         "csgo_item_desc_ak47"),
    ("weapon_aug",                  "sfui_wpnhud_aug",                          "csgo_item_desc_aug"),
    ("weapon_awp",                  "sfui_wpnhud_awp",                          "csgo_item_desc_awp"),
    ("weapon_bayonet",              "sfui_wpnhud_knifebayonet",                 "csgo_item_desc_knife_bayonet"),
    ("weapon_bizon",                "sfui_wpnhud_bizon",                        "csgo_item_desc_bizon"),
    ("weapon_c4",                   "sfui_wpnhud_c4",                           "csgo_item_desc_c4"),
    ("weapon_cz75a",                "sfui_wpnhud_cz75",                         "csgo_item_desc_cz75a"),
    ("weapon_deagle",               "sfui_wpnhud_deagle",                       "csgo_item_desc_deserteagle"),
    ("weapon_decoy",                "sfui_wpnhud_decoy",                        "csgo_item_desc_decoy"),
    ("weapon_elite",                "sfui_wpnhud_elite",                        "csgo_item_desc_elites"),
    ("weapon_famas",                "sfui_wpnhud_famas",                        "csgo_item_desc_famas"),
    ("weapon_fiveseven",            "sfui_wpnhud_fiveseven",                    "csgo_item_desc_fiveseven"),
    ("weapon_flashbang",            "sfui_wpnhud_flashbang",                    "csgo_item_desc_flashbang"),
    ("weapon_g3sg1",                "sfui_wpnhud_g3sg1",                        "csgo_item_desc_g3sg1"),
    ("weapon_galilar",              "sfui_wpnhud_galilar",                      "csgo_item_desc_galilar"),
    ("weapon_glock",                "sfui_wpnhud_glock18",                      "csgo_item_desc_glock18"),
    ("weapon_healthshot",           "sfui_wpnhud_healthshot",                   "csgo_item_desc_healthshot"),
    ("weapon_hegrenade",            "sfui_wpnhud_hegrenade",                    "csgo_item_desc_hegrenade"),
    ("weapon_hkp2000",              "sfui_wpnhud_hkp2000",                      "csgo_item_desc_hkp2000"),
    ("weapon_incgrenade",           "sfui_wpnhud_incgrenade",                   "csgo_item_desc_incgrenade"),
    ("weapon_knife_butterfly",      "sfui_wpnhud_knife_butterfly",              "csgo_item_desc_knife_butterfly"),
    ("weapon_knife_canis",          "sfui_wpnhud_knife_canis",                  "csgo_item_desc_knife_canis"),
    ("weapon_knife_cord",           "sfui_wpnhud_knife_cord",                   "csgo_item_desc_knife_cord"),
    ("weapon_knife_css",            "sfui_wpnhud_knifecss",                     "csgo_item_desc_knife_css"),
    ("weapon_knife_falchion",       "sfui_wpnhud_knife_falchion_advanced",      "csgo_item_desc_knife_falchion_advanced"),
    ("weapon_knife_flip",           "sfui_wpnhud_knifeflip",                    "csgo_item_desc_knifeflip"),
    ("weapon_knife_gut",            "sfui_wpnhud_knifegut",                     "csgo_item_desc_knifegut"),
    ("weapon_knife_gypsy_jackknife","sfui_wpnhud_knife_gypsy_jackknife",        "csgo_item_desc_knife_gypsy_jackknife"),
    ("weapon_knife_karambit",       "sfui_wpnhud_knifekaram",                   "csgo_item_desc_knife_karam"),
    ("weapon_knife_kukri",          "sfui_wpnhud_knife_kukri",                  "csgo_item_desc_knife_kukri"),
    ("weapon_knife_m9_bayonet",     "sfui_wpnhud_knifem9",                      "csgo_item_desc_knifem9"),
    ("weapon_knife_outdoor",        "sfui_wpnhud_knife_outdoor",                "csgo_item_desc_knife_outdoor"),
    ("weapon_knife",                "sfui_wpnhud_knife",                        "csgo_item_desc_knife"),
    ("weapon_knife_push",           "sfui_wpnhud_knife_push",                   "csgo_item_desc_knife_push"),
    ("weapon_knife_skeleton",       "sfui_wpnhud_knife_skeleton",               "csgo_item_desc_knife_skeleton"),
    ("weapon_knife_stiletto",       "sfui_wpnhud_knife_stiletto",               "csgo_item_desc_knife_stiletto"),
    ("weapon_knife_survival_bowie", "sfui_wpnhud_knife_survival_bowie",         "csgo_item_desc_knife_survival_bowie"),
    ("weapon_knife_t",              "sfui_wpnhud_knife_t",                      "csgo_item_desc_knife_t"),
    ("weapon_knife_tactical",       "sfui_wpnhud_knifetactical",                "csgo_item_desc_knifetactical"),
    ("weapon_knife_ursus",          "sfui_wpnhud_knife_ursus",                  "csgo_item_desc_knife_ursus"),
    ("weapon_knife_widowmaker",     "sfui_wpnhud_knife_widowmaker",             "csgo_item_desc_knife_widowmaker"),
    ("weapon_m249",                 "sfui_wpnhud_m249",                         "csgo_item_desc_m249"),
    ("weapon_m4a1",                 "sfui_wpnhud_m4a1",                         "csgo_item_desc_m4a4"),
    ("weapon_m4a1_silencer",        "sfui_wpnhud_m4a1_silencer",                "csgo_item_desc_m4a1_silencer"),
    ("weapon_mac10",                "sfui_wpnhud_mac10",                        "csgo_item_desc_mac10"),
    ("weapon_mag7",                 "sfui_wpnhud_mag7",                         "csgo_item_desc_mag7"),
    ("weapon_molotov",              "sfui_wpnhud_molotov",                      "csgo_item_desc_molotov"),
    ("weapon_mp5sd",                "sfui_wpnhud_mp5sd",                        "csgo_item_desc_mp5sd"),
    ("weapon_mp7",                  "sfui_wpnhud_mp7",                          "csgo_item_desc_mp7"),
    ("weapon_mp9",                  "sfui_wpnhud_mp9",                          "csgo_item_desc_mp9"),
    ("weapon_negev",                "sfui_wpnhud_negev",                        "csgo_item_desc_negev"),
    ("weapon_nova",                 "sfui_wpnhud_nova",                         "csgo_item_desc_nova"),
    ("weapon_p250",                 "sfui_wpnhud_p250",                         "csgo_item_desc_p250"),
    ("weapon_p90",                  "sfui_wpnhud_p90",                          "csgo_item_desc_p90"),
    ("weapon_revolver",             "sfui_wpnhud_revolver",                     "csgo_item_desc_revolver"),
    ("weapon_sawedoff",             "sfui_wpnhud_sawedoff",                     "csgo_item_desc_sawedoff"),
    ("weapon_scar20",               "sfui_wpnhud_scar20",                       "csgo_item_desc_scar20"),
    ("weapon_sg556",                "sfui_wpnhud_sg556",                        "csgo_item_desc_sg553"),
    ("weapon_smokegrenade",         "sfui_wpnhud_smokegrenade",                 "csgo_item_desc_smokegrenade"),
    ("weapon_ssg08",                "sfui_wpnhud_ssg08",                        "csgo_item_desc_ssg08"),
    ("weapon_taser",                "sfui_wpnhud_taser",                        "csgo_item_desc_taser"),
    ("weapon_tec9",                 "sfui_wpnhud_tec9",                         "csgo_item_desc_tec9"),
    ("weapon_ump45",                "sfui_wpnhud_ump45",                        "csgo_item_desc_ump45"),
    ("weapon_usp_silencer",         "sfui_wpnhud_usp_silencer",                 "csgo_item_desc_usp_silencer"),
    ("weapon_xm1014",               "sfui_wpnhud_xm1014",                       "csgo_item_desc_xm1014"),
]


def generate_base_weapons(state: State, translations: Translations) -> list[dict]:
    cdn = state.cdn_images
    result = []

    for weapon_key, name_token, desc_token in _BASE_WEAPON_SPECS:
        image_path = f"econ/weapons/base_weapons/{weapon_key}"
        category_id = get_category(weapon_key)
        result.append({
            "id": f"base_weapon-{weapon_key}",
            "name": translations.t(name_token),
            "description": translations.t(desc_token),
            "def_index": WEAPON_ID_MAPPING[weapon_key],
            "category": {
                "id": category_id,
                "name": translations.t(category_id),
            },
            "image": cdn.get(image_path) or get_image_url(image_path),
        })

    result.sort(key=lambda w: w["def_index"])
    return result

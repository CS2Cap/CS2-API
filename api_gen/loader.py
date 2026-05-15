from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

import storage

from api_gen.constants import (
    RARE_SPECIAL,
    get_image_url,
    get_image_url_svg,
)
from api_gen.state import State
from api_gen.utils import (
    KNIVES,
    filter_unique_by_attribute,
    get_doppler_phase,
    get_graffiti_variations,
    get_player_name_of_highlight,
    is_exclusive,
    is_not_weapon,
)

logger = logging.getLogger(__name__)

# Special collections
SPECIAL_COLLECTIONS = [
    "#CSGO_set_timed_drops_achroma",
    "#CSGO_set_timed_drops_exuberant",
]


def get_collection_image(collection_name: str, image_path: str, cdn_images: dict) -> str:
    """Return the best available image URL for a collection."""
    if image_path in cdn_images:
        return cdn_images[image_path]
    if collection_name in SPECIAL_COLLECTIONS:
        return get_image_url_svg(image_path)
    return get_image_url(image_path)


# get_item_from_key
def get_item_from_key(key: str, state: State) -> Any:
    """Resolve a loot-list key to an item dict (or list for sprays)."""
    items = state.items
    items_game = state.items_game
    rarities = state.rarities
    paint_kits = state.paint_kits
    sticker_kits_obj = state.sticker_kits_obj
    music_definitions_obj = state.music_definitions_obj
    keychain_definitions_obj = state.keychain_definitions_obj

    # Pins
    if "Commodity Pin" in key:
        pin = items.get(key)
        if pin is None:
            return None
        return {
            "id": f"collectible-{pin['object_id']}",
            "name": pin.get("item_name"),
            "rarity": f"rarity_{pin.get('item_rarity', '')}",
            "image": (
                state.cdn_images.get(pin.get("image_inventory", "").lower())
                or get_image_url(pin.get("image_inventory", "").lower())
            ),
        }

    # Agents
    if key.startswith("customplayer_"):
        agent = items.get(key)
        if agent is None:
            return None
        agent_name_lower = agent.get("name", "").lower()
        return {
            "id": f"agent-{agent['object_id']}",
            "name": agent.get("item_name"),
            "rarity": f"rarity_{agent.get('item_rarity', '')}_character",
            "image": (
                state.cdn_images.get(f"econ/characters/{agent_name_lower}")
                or get_image_url(f"econ/characters/{agent_name_lower}")
            ),
        }

    # Regex: [name]type
    match = re.match(r"\[(?P<name>.+?)\](?P<type>.+)", key)
    if not match:
        return None

    name = match.group("name")
    item_type = match.group("type")

    # Special case from Node source
    if name == "cu_bizon_Curse":
        name = name.lower()

    # --- Sticker ---
    if item_type == "sticker":
        sticker = sticker_kits_obj.get(name)
        if sticker is None:
            return None
        return {
            "id": f"{item_type}-{sticker['object_id']}",
            "name": sticker.get("item_name"),
            "rarity": f"rarity_{sticker.get('item_rarity', '')}",
            "image": (
                state.cdn_images.get(f"econ/stickers/{sticker.get('sticker_material', '').lower()}")
                or get_image_url(f"econ/stickers/{sticker.get('sticker_material', '').lower()}")
            ),
        }

    # --- Patch ---
    if item_type == "patch":
        patch = sticker_kits_obj.get(name)
        if patch is None:
            return None
        return {
            "id": f"{item_type}-{patch['object_id']}",
            "name": patch.get("item_name"),
            "rarity": f"rarity_{patch.get('item_rarity', '')}",
            "image": (
                state.cdn_images.get(f"econ/patches/{patch.get('patch_material', '')}")
                or get_image_url(f"econ/patches/{patch.get('patch_material', '')}")
            ),
        }

    # --- Spray / Graffiti ---
    if item_type == "spray":
        graffiti = sticker_kits_obj.get(name)
        if graffiti is None:
            return None
        variations = get_graffiti_variations(name)
        if variations and variations[0] == 0:
            variations_index = list(range(1, 20))  # 1..19
        else:
            variations_index = variations

        if variations_index:
            return [
                {
                    "id": f"graffiti-{graffiti['object_id']}_{idx}",
                    "name": graffiti.get("item_name"),
                    "rarity": f"rarity_{graffiti.get('item_rarity', '')}",
                    "image": (
                        state.cdn_images.get(
                            f"econ/stickers/{graffiti.get('sticker_material', '').lower()}_{idx}"
                        )
                        or get_image_url(
                            f"econ/stickers/{graffiti.get('sticker_material', '').lower()}_{idx}"
                        )
                    ),
                }
                for idx in variations_index
            ]

        return {
            "id": f"graffiti-{graffiti['object_id']}",
            "name": graffiti.get("item_name"),
            "rarity": f"rarity_{graffiti.get('item_rarity', '')}",
            "image": (
                state.cdn_images.get(
                    f"econ/stickers/{graffiti.get('sticker_material', '').lower()}"
                )
                or get_image_url(f"econ/stickers/{graffiti.get('sticker_material', '').lower()}")
            ),
        }

    # --- Music Kit ---
    if item_type == "musickit":
        kit = music_definitions_obj.get(name)
        if kit is None:
            return None
        exclusive = is_exclusive(kit.get("name", ""))
        return {
            "id": f"music_kit-{kit['object_id']}",
            "name": kit.get("loc_name") if exclusive else kit.get("coupon_name"),
            "rarity": "rarity_rare",
            "image": (
                state.cdn_images.get(kit.get("image_inventory", "").lower())
                or get_image_url(kit.get("image_inventory", "").lower())
            ),
        }

    # --- Keychain ---
    if item_type == "keychain":
        keychain = keychain_definitions_obj.get(name)
        if keychain is None:
            return None
        return {
            "id": f"keychain-{keychain['object_id']}",
            "name": keychain.get("loc_name"),
            "rarity": f"rarity_{keychain.get('item_rarity', '')}",
            "image": (
                state.cdn_images.get(keychain.get("image_inventory", "").lower())
                or get_image_url(keychain.get("image_inventory", "").lower())
            ),
        }

    # --- Weapons / Knives / Gloves ---
    glove_types = {
        "studded_bloodhound_gloves",
        "slick_gloves",
        "leather_handwraps",
        "motorcycle_gloves",
        "specialist_gloves",
        "sporty_gloves",
        "studded_hydra_gloves",
        "studded_brokenfang_gloves",
    }

    if "weapon_" in item_type or item_type in glove_types:
        item_id = ""
        item_name: Any = ""
        paint_index = None
        phase = None
        image = None

        item_entry = items.get(item_type)
        translated_name = (
            (
                item_entry.get("item_name_prefab")
                if not is_not_weapon(item_type)
                else (item_entry.get("item_name") if item_entry else None)
            )
            if item_entry
            else None
        )

        is_knife = "weapon_knife" in item_type or "weapon_bayonet" in item_type

        if not is_not_weapon(item_type):
            rarity_entry = rarities.get(key.lower(), {})
            rarity = f"rarity_{rarity_entry.get('rarity', '')}_weapon"
        elif is_knife:
            rarity = "rarity_ancient_weapon"
        else:
            rarity = "rarity_ancient"

        # Vanilla knives
        if name == "vanilla":
            knife = next((k for k in KNIVES if k["name"] == item_type), None)
            if knife is None:
                return None
            item_id = f"skin-vanilla-{item_type}"
            item_name = {
                "tKey": "rare_special_vanilla",
                "weapon": knife["item_name"],
            }
            image = state.cdn_images.get(
                f"econ/weapons/base_weapons/{knife['name']}"
            ) or get_image_url(f"econ/weapons/base_weapons/{knife['name']}")
        else:
            # Find weapon icon
            weapon_icons_entry = None
            for icon_key, icon_val in (
                items_game.get("alternate_icons2", {}).get("weapon_icons", {}).items()
            ):
                if f"{item_type}_{name}_light" in icon_val.get("icon_path", ""):
                    weapon_icons_entry = (icon_key, icon_val)
                    break

            if weapon_icons_entry is None:
                logger.error("[ERROR] Weapon icon not found: %s %s", item_type, name)
                return None

            icon_key, icon_val = weapon_icons_entry
            item_id = f"skin-{icon_key}"

            paint_kit = paint_kits.get(name.lower(), {})

            item_name_dict: dict[str, Any] = {}
            if is_not_weapon(item_type):
                item_name_dict["tKey"] = "rare_special"
            if translated_name:
                item_name_dict["weapon"] = translated_name.replace("#", "")
            item_name_dict["pattern"] = paint_kit.get("description_tag", "").replace("#", "")
            item_name = item_name_dict

            paint_index = paint_kit.get("paint_index")
            phase = (
                get_doppler_phase(int(paint_kit["paint_index"]))
                if paint_kit.get("paint_index") is not None
                else None
            )

            icon_path_lower = icon_val.get("icon_path", "").lower()
            image = (
                state.cdn_images.get(icon_path_lower)
                or state.cdn_images.get(re.sub(r"_light$", "_medium", icon_path_lower))
                or state.cdn_images.get(re.sub(r"_light$", "_heavy", icon_path_lower))
                or get_image_url(icon_path_lower)
            )

        return {
            "id": item_id,
            "name": item_name,
            "rarity": rarity,
            "paint_index": paint_index,
            "phase": phase,
            "image": image,
        }

    logger.error("Unknown item type: %s", item_type)
    return None


# ---------------------------------------------------------------------------
# Individual load_* functions
# ---------------------------------------------------------------------------


def load_items_game(state: State) -> None:
    """Read items_game.json from a local file and patch missing item_sets."""
    data = storage.read_json("static/items_game.json")
    if data is None:
        raise RuntimeError("Could not read static/items_game.json")
    state.items_game = data.get("items_game", data)

    # Patch missing item_sets from client_loot_lists
    sets: dict[str, dict] = {}
    for key, value in state.items_game.get("client_loot_lists", {}).items():
        match = re.match(r"^(sticker_pack_|keychain_pack_)(.+)_(.+)$", key)
        if match:
            first_val_key = next(iter(value), "")
            if "[" in first_val_key:
                set_name = match.group(2)
                if set_name not in sets:
                    sets[set_name] = {
                        "type": match.group(1),
                        "items": {},
                    }
                sets[set_name]["items"].update(value)

    for key, value in sets.items():
        key_translation = key
        if key_translation == "community_2025":
            key_translation = "community2025"
        state.items_game.setdefault("item_sets", {})[f"set_{key}"] = {
            "name": f"#CSGO_set_{key}",
            "name_force": f"#CSGO_crate_{value['type']}{key_translation}_capsule",
            "set_description": f"#CSGO_crate_{value['type']}{key_translation}_capsule_desc",
            "is_collection": 1,
            "items": value["items"],
        }

    # Load default_generated.json (generated by the file tracker from VPK)
    default_generated: list[str] = storage.read_json("static/default_generated.json") or []

    weapon_icons: dict[str, dict] = {}
    for item in default_generated:
        if "light_png.png" not in item:
            continue
        if "pet_hen_1_hen" in item:
            continue
        sha_input = item.replace("_light_png.png", "")
        sha_key = hashlib.sha1(sha_input.encode()).hexdigest()[:12]  # noqa: S324
        icon_path = f"econ/default_generated/{item.replace('_png.png', '')}"
        weapon_icons[sha_key] = {"icon_path": icon_path}

    state.items_game.setdefault("alternate_icons2", {})["weapon_icons"] = weapon_icons


class _BasenameLookup(dict):
    """Dict that extracts the basename from keys on lookup.

    images.json uses basename keys ("weapon_case_generic"), but callers
    pass full image_inventory paths ("econ/weapon_cases/weapon_case_generic").
    This transparently strips the directory prefix on .get() and [] access.
    """

    def get(self, key, default=None):
        if isinstance(key, str) and "/" in key:
            key = key.rsplit("/", 1)[-1]
        return super().get(key, default)

    def __getitem__(self, key):
        if isinstance(key, str) and "/" in key:
            key = key.rsplit("/", 1)[-1]
        return super().__getitem__(key)

    def __contains__(self, key):
        if isinstance(key, str) and "/" in key:
            key = key.rsplit("/", 1)[-1]
        return super().__contains__(key)


def load_images_inventory(state: State) -> None:
    """Load the images index (generated by the file tracker from VPK)."""
    state.cdn_images = _BasenameLookup(storage.read_json("static/images.json") or {})


def load_prefabs(state: State) -> None:
    """Process prefab definitions with inner prefab resolution."""
    prefabs_raw = state.items_game.get("prefabs", {})
    result: dict[str, dict] = {}
    for key, value in prefabs_raw.items():
        inner_prefab = prefabs_raw.get(value.get("prefab", ""))
        result[key] = {
            "item_name": value.get("item_name")
            or (inner_prefab.get("item_name") if inner_prefab else None),
            "item_description": value.get("item_description")
            or (inner_prefab.get("item_description") if inner_prefab else None),
            "first_sale_date": value.get("first_sale_date")
            or (inner_prefab.get("first_sale_date") if inner_prefab else None),
            "prefab": value.get("prefab") or (inner_prefab.get("prefab") if inner_prefab else None),
            "used_by_classes": value.get("used_by_classes"),
        }
    state.prefabs = result


def load_items(state: State) -> None:
    """Process items, merge prefab data."""
    result: dict[str, dict] = {}
    for key, value in state.items_game.get("items", {}).items():
        prefab_data = state.prefabs.get(value.get("prefab", ""))
        result[value.get("name", "")] = {
            **value,
            "object_id": key,
            "item_name": value.get("item_name"),
            "item_description": value.get("item_description"),
            "item_name_prefab": prefab_data.get("item_name") if prefab_data else None,
            "item_description_prefab": prefab_data.get("item_description") if prefab_data else None,
            "used_by_classes": value.get("used_by_classes")
            or (prefab_data.get("used_by_classes") if prefab_data else None),
        }
    state.items = result


def load_item_sets(state: State) -> None:
    """Load item sets as a list of values."""
    state.item_sets = list(state.items_game.get("item_sets", {}).values())


def load_sticker_kits(state: State) -> None:
    """Load sticker kits with Howling Dawn contraband override. Also loads players."""
    kits = []
    for key, item in state.items_game.get("sticker_kits", {}).items():
        item = dict(item)  # shallow copy
        if item.get("name") == "comm01_howling_dawn":
            item["item_rarity"] = "contraband"
        item["object_id"] = key
        kits.append(item)

    state.sticker_kits = kits
    state.sticker_kits_obj = {item["name"]: item for item in kits}

    # Load players from pro_players
    state.players = {
        pid: str(player.get("name", ""))
        for pid, player in state.items_game.get("pro_players", {}).items()
    }


def load_keychain_definitions(state: State) -> None:
    """Load keychain definitions."""
    defs = []
    for key, item in state.items_game.get("keychain_definitions", {}).items():
        entry = dict(item)
        entry["object_id"] = key
        defs.append(entry)

    state.keychain_definitions = defs
    state.keychain_definitions_obj = {item["name"]: item for item in defs}


def load_paint_kits(state: State) -> None:
    """Extract paint kits with wear ranges, style info."""
    result: dict[str, dict] = {}
    for key, item in state.items_game.get("paint_kits", {}).items():
        if item.get("description_tag") is not None:
            result[item["name"].lower()] = {
                "description_tag": item["description_tag"],
                "wear_remap_min": item.get("wear_remap_min", 0.0),
                "wear_remap_max": item.get("wear_remap_max", 1.0),
                "paint_index": key,
                "style_id": item.get("style", 0),
                "style_name": f"SFUI_ItemInfo_FinishStyle_{item.get('style', 0)}",
                "legacy_model": bool(item.get("use_legacy_model"))
                if item.get("use_legacy_model") is not None
                else False,
            }
    state.paint_kits = result


def load_music_definitions(state: State) -> None:
    """Load music definitions."""
    defs = []
    for key, item in state.items_game.get("music_definitions", {}).items():
        entry = dict(item)
        entry["object_id"] = key
        entry["loc_name"] = item.get("loc_name")
        entry["loc_description"] = item.get("loc_description")
        entry["coupon_name"] = f"coupon_{item.get('name', '')}"
        defs.append(entry)

    state.music_definitions = defs
    state.music_definitions_obj = {item["name"]: item for item in defs}


def load_client_loot_lists(state: State) -> None:
    """Load client loot lists directly."""
    state.client_loot_lists = state.items_game.get("client_loot_lists", {})


def load_revolving_loot_lists(state: State) -> None:
    """Load revolving loot lists directly."""
    state.revolving_loot_lists = state.items_game.get("revolving_loot_lists", {})


def load_rarities(state: State) -> None:
    """Parse rarity from loot list names + hardcoded overrides."""
    hard_coded: dict[str, dict[str, str]] = {
        "[cu_m4a1_howling]weapon_m4a1": {"rarity": "contraband"},
        "[cu_retribution]weapon_elite": {"rarity": "rare"},
        "[cu_mac10_decay]weapon_mac10": {"rarity": "mythical"},
        "[cu_p90_scorpius]weapon_p90": {"rarity": "rare"},
        "[hy_labrat_mp5]weapon_mp5sd": {"rarity": "mythical"},
        "[cu_xray_p250]weapon_p250": {"rarity": "mythical"},
        "[cu_usp_spitfire]weapon_usp_silencer": {"rarity": "legendary"},
        "[am_nitrogen]weapon_cz75a": {"rarity": "rare"},
    }

    rarity_set = {"common", "uncommon", "rare", "mythical", "legendary", "ancient"}

    items = dict(hard_coded)
    for name, keys in state.items_game.get("client_loot_lists", {}).items():
        rarity = name.split("_")[-1]
        if rarity in rarity_set:
            for k in keys:
                if "[" in k:
                    items[k.lower()] = {"rarity": rarity}

    state.rarities = items


def load_skins_by_crates(state: State) -> None:
    """Recursive loot list extraction via extract_items() and extract_rare_items()."""
    client_loot_lists = state.client_loot_lists
    revolving_loot_lists = state.revolving_loot_lists

    def extract_items(key: str, loot_lists: dict) -> dict:
        current_object = loot_lists.get(key, {})
        items: dict = {}
        for sub_key in current_object:
            if "[" in sub_key:
                items[sub_key] = current_object[sub_key]
            if "Commodity Pin" in sub_key:
                items[sub_key] = current_object[sub_key]
            items.update(extract_items(sub_key, loot_lists))
        return items

    def extract_rare_items(key: str, loot_lists: dict) -> list[str]:
        current_object = loot_lists.get(key, {})
        for sub_key in current_object:
            if sub_key in RARE_SPECIAL:
                return list(RARE_SPECIAL[sub_key].keys())
        return []

    result: dict[str, list] = {}

    for item_value in revolving_loot_lists.values():
        if item_value == "crate_dhw13_promo":
            # Source: https://counterstrike.fandom.com/wiki/DreamHack_2013_Souvenir_Package
            dhw_sets = [
                "set_dust_2",
                "set_safehouse",
                "set_italy",
                "set_lake",
                "set_train",
                "set_mirage",
            ]
            crate_items = []
            for s in dhw_sets:
                for k in extract_items(s, client_loot_lists):
                    resolved = get_item_from_key(k, state)
                    if resolved is not None:
                        crate_items.append(resolved)
            revolver_item = get_item_from_key("[sp_tape]weapon_revolver", state)
            if revolver_item is not None:
                crate_items.append(revolver_item)
            result[item_value] = crate_items
            continue

        if item_value == "crate_ems14_promo":
            ems_sets = [
                "set_dust_2",
                "set_safehouse",
                "set_italy",
                "set_lake",
                "set_train",
                "set_mirage",
            ]
            crate_items = []
            for s in ems_sets:
                for k in extract_items(s, client_loot_lists):
                    resolved = get_item_from_key(k, state)
                    if resolved is not None:
                        crate_items.append(resolved)
            result[item_value] = crate_items
            continue

        crate_items = []
        for k in extract_items(item_value, client_loot_lists):
            resolved = get_item_from_key(k, state)
            if resolved is not None:
                crate_items.append(resolved)

        # StatTrak music kits
        if "_stattrak_" in item_value and "musickit" in item_value:
            crate_items = [
                {
                    **ci,
                    "id": f"{ci['id']}_st",
                    "name": f"{ci['name']}_stattrak",
                }
                for ci in crate_items
            ]

        result[item_value] = crate_items

    # Hardcoded: set_xraymachine
    xray_item = get_item_from_key("[cu_xray_p250]weapon_p250", state)
    if xray_item is not None:
        result["set_xraymachine"] = [xray_item]

    # Rare special items
    for item_value in revolving_loot_lists.values():
        rare_items = []
        for k in extract_rare_items(item_value, client_loot_lists):
            resolved = get_item_from_key(k, state)
            if resolved is not None:
                rare_items.append(resolved)
        result[f"rare--{item_value}"] = rare_items

    state.skins_by_crates = result


def load_crates_by_skins(state: State) -> None:
    """Build reverse mapping from skin id -> list of crates."""
    hard_coded_crates = {
        "set_xraymachine": {
            "object_id": 4668,
            "item_name": "#CSGO_set_xraymachine",
            "image_inventory": "econ/weapon_cases/crate_xray_p250",
        },
    }

    acc: dict[str, list] = {}
    for crate_key, items_list in state.skins_by_crates.items():
        clean_key = crate_key.replace("rare--", "")

        for item in items_list:
            if item is None:
                continue
            item_id = item.get("id")
            if item_id is None:
                continue
            if item_id not in acc:
                acc[item_id] = []

            # Find the revolving loot list entry for this crate
            loot_list = None
            for ll_id, ll_item in state.revolving_loot_lists.items():
                if ll_item == clean_key:
                    loot_list = (ll_id, ll_item)
                    break

            crate_item = hard_coded_crates.get(clean_key)
            if crate_item is None:
                crate_item = state.items.get(clean_key)
            if crate_item is None and loot_list is not None:
                for i_val in state.items.values():
                    attrs = i_val.get("attributes", {})
                    supply_crate = attrs.get("set supply crate series", {})
                    # JS uses == (loose equality) so compare as strings
                    if str(supply_crate.get("value", "")) == str(loot_list[0]):
                        crate_item = i_val
                        break

            if crate_item is not None:
                img_inv = (crate_item.get("image_inventory") or "").lower()
                acc[item_id].append(
                    {
                        "id": f"crate-{crate_item.get('object_id', '')}",
                        "name": crate_item.get("item_name"),
                        "image": state.cdn_images.get(img_inv) or get_image_url(img_inv),
                    }
                )

    state.crates_by_skins = acc


def load_skins_by_collections(state: State) -> None:
    """Build mapping from collection key -> list of items.

    Includes 3 hardcoded spray collections.
    """
    # Seed with hardcoded spray collections
    spray_std2_1_keys = [
        "[spray_std2_applause]spray",
        "[spray_std2_beep]spray",
        "[spray_std2_boom]spray",
        "[spray_std2_brightstar]spray",
        "[spray_std2_brokenheart]spray",
        "[spray_std2_chef_kiss]spray",
        "[spray_std2_chick]spray",
        "[spray_std2_chunkychicken]spray",
        "[spray_std2_goofy]spray",
        "[spray_std2_grimace]spray",
        "[spray_std2_happy_cat]spray",
        "[spray_std2_hop]spray",
        "[spray_std2_kiss]spray",
        "[spray_std2_lightbulb]spray",
        "[spray_std2_little_crown]spray",
        "[spray_std2_omg]spray",
        "[spray_std2_silverbullet]spray",
        "[spray_std2_smirk]spray",
        "[spray_std2_thoughtfull]spray",
    ]

    spray_std2_2_keys = [
        "[spray_std2_1g]spray",
        "[spray_std2_200iq]spray",
        "[spray_std2_bubble_denied]spray",
        "[spray_std2_bubble_question]spray",
        "[spray_std2_choke]spray",
        "[spray_std2_dead_now]spray",
        "[spray_std2_fart]spray",
        "[spray_std2_little_ez]spray",
        "[spray_std2_littlebirds]spray",
        "[spray_std2_nt]spray",
        "[spray_std2_okay]spray",
        "[spray_std2_oops]spray",
        "[spray_std2_puke]spray",
        "[spray_std2_rly]spray",
        "[spray_std2_smarm]spray",
        "[spray_std2_smooch]spray",
        "[spray_std2_uhoh]spray",
    ]

    spray_std3_keys = [
        "[spray_std3_ak47]spray",
        "[spray_std3_aug]spray",
        "[spray_std3_awp]spray",
        "[spray_std3_bizon]spray",
        "[spray_std3_cz]spray",
        "[spray_std3_famas]spray",
        "[spray_std3_galil]spray",
        "[spray_std3_m4a1]spray",
        "[spray_std3_m4a4]spray",
        "[spray_std3_mac10]spray",
        "[spray_std3_mp7]spray",
        "[spray_std3_mp9]spray",
        "[spray_std3_p90]spray",
        "[spray_std3_sg553]spray",
        "[spray_std3_ump]spray",
        "[spray_std3_xm1014]spray",
    ]

    def _flatten_spray_keys(keys: list[str]) -> list:
        result = []
        for k in keys:
            resolved = get_item_from_key(k, state)
            if resolved is None:
                continue
            # Sprays return a list (variations), spread them
            if isinstance(resolved, list):
                result.extend(resolved)
            else:
                result.append(resolved)
        return result

    initial: dict[str, list] = {
        "selfopeningitem_crate_spray_std2_1": _flatten_spray_keys(spray_std2_1_keys),
        "selfopeningitem_crate_spray_std2_2": _flatten_spray_keys(spray_std2_2_keys),
        "selfopeningitem_crate_spray_std3": _flatten_spray_keys(spray_std3_keys),
    }

    result = dict(initial)
    for key, value in state.items_game.get("item_sets", {}).items():
        items_list = []
        for item_key in value.get("items", {}):
            resolved = get_item_from_key(item_key, state)
            if resolved is not None:
                items_list.append(resolved)
        result[key] = items_list

    state.skins_by_collections = result


def load_crates_by_collections(state: State) -> None:
    """Build mapping from collection -> list of crates.

    Note: Node source has a reduce() bug with missing initial value;
    we initialize to {} explicitly.
    """
    acc: dict[str, list] = {}
    for collection, items in state.skins_by_collections.items():
        item_ids = list({item.get("id") for item in items if item and item.get("id")})
        crates = []
        for iid in item_ids:
            crates.extend(state.crates_by_skins.get(iid, []))
        acc[collection] = filter_unique_by_attribute(crates, "id")

    state.crates_by_collections = acc


def load_collections_by_skins(state: State) -> None:
    """Build reverse mapping from skin id -> list of collections."""
    acc: dict[str, list] = {}
    for crate_key, items_list in state.skins_by_collections.items():
        clean_key = crate_key.replace("rare--", "")

        for item in items_list:
            if item is None:
                continue
            item_id = item.get("id")
            if item_id is None:
                continue
            if item_id not in acc:
                acc[item_id] = []

            crate_item = state.items_game.get("item_sets", {}).get(clean_key)
            if crate_item is not None:
                file_name = crate_item.get("name", "").replace("#CSGO_", "")
                image_path = f"econ/set_icons/{file_name}"
                image = get_collection_image(
                    crate_item.get("name", ""), image_path, state.cdn_images
                )

                acc[item_id].append(
                    {
                        "id": f"collection-{file_name.replace('_', '-')}",
                        "name": crate_item.get("name_force") or crate_item.get("name"),
                        "image": image,
                    }
                )

    state.collections_by_skins = acc


def load_collections_by_stickers(state: State) -> None:
    """Build mapping from sticker id -> list of collections they belong to."""
    acc: dict[str, list] = {}

    for collection_key, item_set in state.items_game.get("item_sets", {}).items():
        if not item_set.get("is_collection"):
            continue
        item_keys = list(item_set.get("items", {}).keys())
        has_stickers = any("[" in ik and "]sticker" in ik for ik in item_keys)
        if not has_stickers:
            continue

        for item_key in item_keys:
            if "[" not in item_key or "]sticker" not in item_key:
                continue
            sticker_item = get_item_from_key(item_key, state)
            if sticker_item is None or not isinstance(sticker_item, dict):
                continue
            sticker_id = sticker_item.get("id")
            if not sticker_id:
                continue
            if sticker_id not in acc:
                acc[sticker_id] = []

            file_name = collection_key.replace("set_", "")
            image_path = f"econ/set_icons/set_{file_name}"
            image = get_collection_image(item_set.get("name", ""), image_path, state.cdn_images)

            acc[sticker_id].append(
                {
                    "id": f"collection-set-{file_name.replace('_', '-')}",
                    "name": item_set.get("name_force") or item_set.get("name"),
                    "image": image,
                }
            )

    state.collections_by_stickers = acc


def load_souvenir_skins(state: State) -> None:
    """Build set of skin IDs that have souvenir variants."""
    souvenir_items: dict[str, bool] = {}

    for item in state.items.values():
        prefab = item.get("prefab", "")
        if prefab == "weapon_case_souvenirpkg" or (
            isinstance(prefab, str) and "_souvenir_crate_promo_prefab" in prefab
        ):
            loot_list_name = item.get("loot_list_name")
            attribute_value = (
                item.get("attributes", {}).get("set supply crate series", {}).get("value")
            )
            key_loot_list = loot_list_name or state.revolving_loot_lists.get(
                str(attribute_value) if attribute_value is not None else ""
            )

            tag_value = item.get("tags", {}).get("ItemSet", {}).get("tag_value")
            skins = (
                state.skins_by_crates.get(tag_value, [])
                if tag_value and tag_value in state.skins_by_crates
                else state.skins_by_crates.get(key_loot_list, [])
            )

            for skin in skins:
                if skin and skin.get("id"):
                    souvenir_items[skin["id"]] = True

    # Hardcoded: MP5-SD | Lab Rats
    souvenir_items["skin-e73d6e7e9004"] = True

    state.souvenir_skins = souvenir_items


def load_stattrak_skins(state: State) -> None:
    """Build set of loot-list keys that support StatTrak."""
    item_sets = state.item_sets
    items = state.items

    crates: dict[str, bool] = {}
    for item in items.values():
        prefab = (item.get("prefab") or "").split(" ")
        if (
            "weapon_case" in prefab
            or "volatile_pricing" in prefab
            or "volatile_pricing_gloves" in prefab
        ):
            name = (item.get("tags") or {}).get("ItemSet", {}).get("tag_value")
            if name is not None:
                crates[name] = True

    result: dict[str, bool] = {
        "[cu_m4a1_howling]weapon_m4a1": True,
        "[cu_xray_p250]weapon_p250": True,
    }

    skip_collections = ["#CSGO_set_dust_2_2021"]

    for item_set in item_sets:
        if item_set.get("is_collection") and item_set.get("name") not in skip_collections:
            set_name = item_set.get("name", "").replace("#CSGO_", "")
            if set_name in crates:
                for k in item_set.get("items", {}):
                    result[k.lower()] = True

    state.stattrak_skins = result


def load_highlights(state: State) -> None:
    """Load highlight reels."""
    reels = []
    for reel_id, item in state.items_game.get("highlight_reels", {}).items():
        tournament_string = str(item.get("tournament event id", "")).zfill(3)
        team0 = str(item.get("tournament event team0 id", "")).zfill(3)
        team1 = str(item.get("tournament event team1 id", "")).zfill(3)
        stage = str(item.get("tournament event stage id", "")).zfill(3)
        match_string = f"{team0}v{team1}_{stage}"

        item_id = item.get("id", "")
        map_name = item.get("map", "")

        video = (
            f"https://cdn.steamstatic.com/apps/csgo/videos/highlightreels/"
            f"{tournament_string}/{match_string}/"
            f"{tournament_string}_{match_string}_{map_name}_{item_id}_ww_1080p.webm"
        )

        id_prefix = item_id.split("_")[0] if "_" in str(item_id) else str(item_id)

        reels.append(
            {
                "id": item_id,
                "highlight_reel": reel_id,
                "tournament_event_id": item.get("tournament event id"),
                "tournament_event_team0_id": item.get("tournament event team0 id"),
                "tournament_event_team1_id": item.get("tournament event team1 id"),
                "tournament_event_stage_id": item.get("tournament event stage id"),
                "tournament_event_map": map_name,
                "tournament_player": get_player_name_of_highlight(item_id, state.players),
                "image": get_image_url(f"econ/keychains/{id_prefix}/kc_{id_prefix}"),
                "image_inventory": f"econ/keychains/{id_prefix}/kc_{id_prefix}",
                "video": video,
                # This asset is not hosted on the public CDN; keep the path relative.
                "thumbnail": f"/highlightreels/ww/{reel_id}.webp",
            }
        )

    state.highlight_reels = reels


def load_pro_teams(state: State) -> None:
    """Load professional teams."""
    result: dict[str, dict] = {}
    for team_id, item in state.items_game.get("pro_teams", {}).items():
        result[team_id] = {
            "id": int(team_id),
            "tag": item.get("tag"),
            "geo": item.get("geo"),
        }
    state.pro_teams = result


def load_pro_players(state: State) -> None:
    """Load professional players."""
    result: dict[str, dict] = {}
    for player_id, item in state.items_game.get("pro_players", {}).items():
        result[player_id] = {
            "id": int(player_id),
            "name": item.get("name"),
            "code": item.get("code"),
            "dob": item.get("dob"),
            "geo": item.get("geo"),
        }
    state.pro_players = result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def load_data(state: State) -> None:
    """Load all data into state, following the exact order from main.js."""
    load_items_game(state)
    load_images_inventory(state)
    load_prefabs(state)
    load_items(state)
    load_item_sets(state)
    load_sticker_kits(state)
    load_keychain_definitions(state)
    load_paint_kits(state)
    load_music_definitions(state)
    load_client_loot_lists(state)
    load_revolving_loot_lists(state)
    load_rarities(state)
    load_skins_by_crates(state)
    load_crates_by_skins(state)
    load_skins_by_collections(state)
    load_crates_by_collections(state)
    load_collections_by_skins(state)
    load_collections_by_stickers(state)
    load_souvenir_skins(state)
    load_stattrak_skins(state)
    load_highlights(state)
    load_pro_teams(state)
    load_pro_players(state)

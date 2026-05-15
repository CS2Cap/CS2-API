from __future__ import annotations


def generate_inventory(results: dict[str, list[dict]]) -> dict:
    """Build the inventory structure from per-category item lists.

    Expected keys (all optional; skipped if missing):
        ``skins``, ``crates``, ``collectibles``, ``stickers``, ``graffiti``,
        ``music_kits``, ``keychains``, ``highlights``, ``agents``, ``patches``,
        ``keys``, ``sticker_slabs``, ``tools``.
    """
    items: dict = {}

    # ------------------------------------------------------------------
    # skins
    # ------------------------------------------------------------------
    for skin in results.get("skins") or []:
        weapon = skin.get("weapon") or {}
        weapon_id = weapon.get("weapon_id")
        if weapon_id is None:
            continue
        paint_index = skin.get("paint_index")
        paint_key = "null" if paint_index is None else paint_index
        if "skins" not in items:
            items["skins"] = {}
        if weapon_id not in items["skins"]:
            items["skins"][weapon_id] = {}
        items["skins"][weapon_id][paint_key] = {
            "name": skin.get("name"),
            "rarity": skin.get("rarity"),
            "marketable": True,
            "image": skin.get("image"),
        }

    # ------------------------------------------------------------------
    # crates
    # ------------------------------------------------------------------
    for crate in results.get("crates") or []:
        crate_id = (crate.get("id") or "").replace("crate-", "")
        if not crate_id:
            continue
        if "crates" not in items:
            items["crates"] = {}
        items["crates"][crate_id] = {
            "name": crate.get("name"),
            "rarity": crate.get("rarity"),
            "marketable": bool(crate.get("market_hash_name")),
            "image": crate.get("image"),
        }

    # ------------------------------------------------------------------
    # collectibles
    # ------------------------------------------------------------------
    for collectible in results.get("collectibles") or []:
        col_id = (collectible.get("id") or "").replace("collectible-", "")
        if not col_id:
            continue
        if "collectibles" not in items:
            items["collectibles"] = {}
        items["collectibles"][col_id] = {
            "name": collectible.get("name"),
            "rarity": collectible.get("rarity"),
            "marketable": bool(collectible.get("market_hash_name")),
            "image": collectible.get("image"),
        }

    # ------------------------------------------------------------------
    # stickers
    # ------------------------------------------------------------------
    for sticker in results.get("stickers") or []:
        sticker_id = (sticker.get("id") or "").replace("sticker-", "")
        if not sticker_id:
            continue
        if "stickers" not in items:
            items["stickers"] = {}
        items["stickers"][sticker_id] = {
            "name": sticker.get("name"),
            "rarity": sticker.get("rarity"),
            "marketable": bool(sticker.get("market_hash_name")),
            "image": sticker.get("image"),
        }

    # ------------------------------------------------------------------
    # graffiti
    # ------------------------------------------------------------------
    for graffiti in results.get("graffiti") or []:
        graffiti_id = (graffiti.get("id") or "").replace("graffiti-", "")
        if not graffiti_id:
            continue
        if "graffiti" not in items:
            items["graffiti"] = {}
        items["graffiti"][graffiti_id] = {
            "name": graffiti.get("name"),
            "rarity": graffiti.get("rarity"),
            "marketable": bool(graffiti.get("market_hash_name")),
            "image": graffiti.get("image"),
        }

    # ------------------------------------------------------------------
    # music_kits
    # ------------------------------------------------------------------
    for music_kit in results.get("music_kits") or []:
        mk_id_raw = music_kit.get("id") or ""
        if "_st" in mk_id_raw:
            continue
        mk_id = mk_id_raw.replace("music_kit-", "")
        if not mk_id:
            continue
        if "music_kits" not in items:
            items["music_kits"] = {}
        items["music_kits"][mk_id] = {
            "name": music_kit.get("name"),
            "rarity": music_kit.get("rarity"),
            "marketable": bool(music_kit.get("market_hash_name")),
            "image": music_kit.get("image"),
        }

    # ------------------------------------------------------------------
    # keychains
    # ------------------------------------------------------------------
    for keychain in results.get("keychains") or []:
        kc_id = (keychain.get("id") or "").replace("keychain-", "")
        if not kc_id:
            continue
        if "keychains" not in items:
            items["keychains"] = {}
        items["keychains"][kc_id] = {
            "name": keychain.get("name"),
            "rarity": keychain.get("rarity"),
            "marketable": bool(keychain.get("market_hash_name")),
            "image": keychain.get("image"),
        }

    # ------------------------------------------------------------------
    # highlights
    # ------------------------------------------------------------------
    for highlight in results.get("highlights") or []:
        hl_id = (highlight.get("id") or "").replace("highlight-", "")
        if not hl_id:
            continue
        if "highlights" not in items:
            items["highlights"] = {}
        items["highlights"][hl_id] = {
            "name": highlight.get("name"),
            "rarity": highlight.get("rarity"),  # may be None
            "marketable": bool(highlight.get("market_hash_name")),
            "image": highlight.get("image"),
        }

    # ------------------------------------------------------------------
    # agents
    # ------------------------------------------------------------------
    for agent in results.get("agents") or []:
        agent_id = (agent.get("id") or "").replace("agent-", "")
        if not agent_id:
            continue
        if "agents" not in items:
            items["agents"] = {}
        items["agents"][agent_id] = {
            "name": agent.get("name"),
            "rarity": agent.get("rarity"),
            "marketable": bool(agent.get("market_hash_name")),
            "image": agent.get("image"),
        }

    # ------------------------------------------------------------------
    # patches
    # ------------------------------------------------------------------
    for patch in results.get("patches") or []:
        patch_id = (patch.get("id") or "").replace("patch-", "")
        if not patch_id:
            continue
        if "patches" not in items:
            items["patches"] = {}
        items["patches"][patch_id] = {
            "name": patch.get("name"),
            "rarity": patch.get("rarity"),
            "marketable": bool(patch.get("market_hash_name")),
            "image": patch.get("image"),
        }

    # ------------------------------------------------------------------
    # keys
    # ------------------------------------------------------------------
    for key in results.get("keys") or []:
        key_id = (key.get("id") or "").replace("key-", "")
        if not key_id:
            continue
        if "keys" not in items:
            items["keys"] = {}
        items["keys"][key_id] = {
            "name": key.get("name"),
            "rarity": key.get("rarity"),  # may be None
            "marketable": bool(key.get("market_hash_name")),
            "image": key.get("image"),
        }

    # ------------------------------------------------------------------
    # sticker_slabs
    # ------------------------------------------------------------------
    for slab in results.get("sticker_slabs") or []:
        slab_id = (slab.get("id") or "").replace("sticker_slab-", "")
        if not slab_id:
            continue
        if "sticker_slabs" not in items:
            items["sticker_slabs"] = {}
        items["sticker_slabs"][slab_id] = {
            "name": slab.get("name"),
            "rarity": slab.get("rarity"),
            "marketable": bool(slab.get("market_hash_name")),
            "image": slab.get("image"),
        }

    # ------------------------------------------------------------------
    # tools
    # ------------------------------------------------------------------
    for tool in results.get("tools") or []:
        tool_id = (tool.get("id") or "").replace("tool-", "")
        if not tool_id:
            continue
        if "tools" not in items:
            items["tools"] = {}
        items["tools"][tool_id] = {
            "name": tool.get("name"),
            "rarity": tool.get("rarity"),  # may be None
            "marketable": bool(tool.get("market_hash_name")),
            "image": tool.get("image"),
        }

    return items

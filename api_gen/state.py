"""Central state object populated by loader, consumed by item generators."""
from dataclasses import dataclass, field


@dataclass
class State:
    items_game: dict = field(default_factory=dict)
    cdn_images: dict = field(default_factory=dict)
    prefabs: dict = field(default_factory=dict)
    items: dict = field(default_factory=dict)
    item_sets: list = field(default_factory=list)
    sticker_kits: list = field(default_factory=list)
    sticker_kits_obj: dict = field(default_factory=dict)
    keychain_definitions: list = field(default_factory=list)
    keychain_definitions_obj: dict = field(default_factory=dict)
    paint_kits: dict = field(default_factory=dict)
    music_definitions: list = field(default_factory=list)
    music_definitions_obj: dict = field(default_factory=dict)
    client_loot_lists: dict = field(default_factory=dict)
    revolving_loot_lists: dict = field(default_factory=dict)
    rarities: dict = field(default_factory=dict)
    skins_by_crates: dict = field(default_factory=dict)
    crates_by_skins: dict = field(default_factory=dict)
    skins_by_collections: dict = field(default_factory=dict)
    crates_by_collections: dict = field(default_factory=dict)
    collections_by_skins: dict = field(default_factory=dict)
    collections_by_stickers: dict = field(default_factory=dict)
    souvenir_skins: dict = field(default_factory=dict)
    stattrak_skins: dict = field(default_factory=dict)
    players: dict = field(default_factory=dict)
    pro_teams: dict = field(default_factory=dict)
    pro_players: dict = field(default_factory=dict)
    highlight_reels: list = field(default_factory=list)

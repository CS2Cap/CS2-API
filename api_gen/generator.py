import argparse
import os
import sys

import storage
from dotenv import load_dotenv

from api_gen.constants import LANGUAGES
from api_gen.items.agents import generate_agents
from api_gen.items.base_weapons import generate_base_weapons
from api_gen.items.collectibles import generate_collectibles
from api_gen.items.collections import generate_collections
from api_gen.items.crates import generate_crates
from api_gen.items.graffiti import generate_graffiti
from api_gen.items.highlights import generate_highlights
from api_gen.items.inventory import generate_inventory
from api_gen.items.keychains import generate_keychains
from api_gen.items.keys import generate_keys
from api_gen.items.music_kits import generate_music_kits
from api_gen.items.patches import generate_patches
from api_gen.items.skins import generate_skins
from api_gen.items.skins_not_grouped import generate_skins_not_grouped
from api_gen.items.sticker_slabs import generate_sticker_slabs
from api_gen.items.stickers import generate_stickers
from api_gen.items.tools import generate_tools
from api_gen.loader import load_data
from api_gen.state import State
from api_gen.translations import Translations

STATIC_DIR = "static"
OUTPUT_DIR = "output"


GENERATORS = [
    ("agents", generate_agents),
    ("base_weapons", generate_base_weapons),
    ("collectibles", generate_collectibles),
    ("collections", generate_collections),
    ("crates", generate_crates),
    ("graffiti", generate_graffiti),
    ("highlights", generate_highlights),
    ("keychains", generate_keychains),
    ("keys", generate_keys),
    ("music_kits", generate_music_kits),
    ("patches", generate_patches),
    ("skins", generate_skins),
    ("skins_not_grouped", generate_skins_not_grouped),
    ("sticker_slabs", generate_sticker_slabs),
    ("stickers", generate_stickers),
    ("tools", generate_tools),
]

# Categories included in all.json, matching group.js inputFilePathsTemplate order.
# Excludes: skins (grouped), base_weapons, highlights, inventory.
ALL_JSON_CATEGORIES = {
    "agents",
    "collectibles",
    "collections",
    "crates",
    "graffiti",
    "keys",
    "music_kits",
    "patches",
    "skins_not_grouped",
    "stickers",
    "sticker_slabs",
    "keychains",
    "tools",
}


def build_all_json(results: dict[str, list]) -> dict[str, dict]:
    """Compose the flat ``all.json`` mapping from per-category generator results.

    Only categories listed in :data:`ALL_JSON_CATEGORIES` contribute. Each item
    must be a dict with an ``id`` field; later items with the same id overwrite
    earlier ones, matching ``group.js`` semantics.
    """
    all_data: dict[str, dict] = {}
    for category_name, items in results.items():
        if category_name not in ALL_JSON_CATEGORIES:
            continue
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "id" in item:
                all_data[item["id"]] = item
    return all_data


def _select_languages(codes: list[str]) -> list[dict[str, str]]:
    """Resolve a list of folder codes (or 'all') against the LANGUAGES table."""
    if any(c.lower() == "all" for c in codes):
        return list(LANGUAGES)
    selected = [lang for lang in LANGUAGES if lang["folder"] in codes]
    unknown = [c for c in codes if c not in {lang["folder"] for lang in LANGUAGES}]
    if unknown:
        print(f"Warning: unknown language codes ignored: {', '.join(unknown)}")
    return selected


def _generate_for_language(
    state: State,
    lang: dict[str, str],
    en_data: dict,
) -> None:
    """Generate every category for a single language."""
    folder = lang["folder"]
    lang_file = f"csgo_{lang['language']}.json"

    if folder == "en":
        lang_data = en_data
    else:
        lang_data = storage.read_json(os.path.join(STATIC_DIR, lang_file))
        if lang_data is None:
            print(f"Skipping {folder}: missing {STATIC_DIR}/{lang_file}")
            return

    translations = Translations()
    translations.load_from_json(en_data, lang_data)
    translations.set_language(folder)

    out_dir = os.path.join(OUTPUT_DIR, folder)

    results: dict[str, list] = {}
    for name, generate_fn in GENERATORS:
        print(f"  [{folder}] generating {name}...")
        data = generate_fn(state, translations)
        results[name] = data
        storage.write_json(os.path.join(out_dir, f"{name}.json"), data)

    print(f"  [{folder}] generating inventory...")
    inv = generate_inventory(results)
    storage.write_json(os.path.join(out_dir, "inventory.json"), inv)

    storage.write_json(os.path.join(out_dir, "all.json"), build_all_json(results))


def run(force: bool = False, language_codes: list[str] | None = None) -> None:
    load_dotenv()

    latest_manifest = storage.read(os.path.join(STATIC_DIR, "manifestId.txt"))
    if latest_manifest:
        latest_manifest = latest_manifest.strip()

    existing_manifest = storage.read(os.path.join(OUTPUT_DIR, "manifestId.txt"))
    if existing_manifest:
        existing_manifest = existing_manifest.strip()

    if not force:
        if latest_manifest == existing_manifest:
            print("No changes detected, exiting")
            return
        print("Manifest ID changed, generating new data.")

    languages = _select_languages(language_codes or ["en"])
    if not languages:
        print("Error: no valid languages selected.")
        sys.exit(1)

    print("Loading game data...")
    state = State()
    load_data(state)

    print("Loading default English translations...")
    en_data = storage.read_json(os.path.join(STATIC_DIR, "csgo_english.json"))
    if en_data is None:
        print(f"Error: missing {STATIC_DIR}/csgo_english.json")
        sys.exit(1)

    for lang in languages:
        print(f"Language: {lang['language']} ({lang['folder']})")
        _generate_for_language(state, lang, en_data)

    storage.write(os.path.join(OUTPUT_DIR, "manifestId.txt"), latest_manifest or "")

    print("API generation complete")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the CS2 API JSON files.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even when the manifest hasn't changed.",
    )
    parser.add_argument(
        "--languages",
        default="en",
        help=(
            "Comma-separated folder codes (e.g. en,ru,uk) or 'all'. "
            "Defaults to 'en'."
        ),
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    codes = [c.strip() for c in args.languages.split(",") if c.strip()]
    run(force=args.force, language_codes=codes)

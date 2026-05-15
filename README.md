# CS2-API

A Python rewrite of [ByMykel](https://github.com/ByMykel)'s [CSGO-API](https://github.com/ByMykel/CSGO-API) and [counter-strike-file-tracker](https://github.com/ByMykel/counter-strike-file-tracker). Tracks Counter-Strike 2 game files from Steam and generates a structured JSON API for all in-game items.

## What it does

**File Tracker** — Logs into Steam, detects game updates via manifest changes, downloads VPK archives, and extracts game data (translations, item definitions, and optionally panorama images).

**API Generator** — Parses the extracted game data and produces JSON files for every item category: skins, stickers, agents, crates, collections, music kits, keychains, patches, graffiti, keys, collectibles, tools, highlights, and more.

### Key features

- Incremental updates — only downloads changed shards using CRC32 diffing
- 28 languages supported with English fallback
- Valve texture decoding (DXT5/BC3, BGRA8888, embedded PNG, compiled SVG)
- Image extraction is opt-in (it needs tens of GB of temporary disk)
- Change detection via Steam depot manifest IDs

## Project structure

```bash
CS2-API/
├── file_tracker/          # Steam file tracking & extraction
│   ├── steam_client.py    # Steam login and manifest retrieval
│   ├── tracker.py         # Main orchestrator
│   ├── vpk_extractor.py   # VPK download, CRC diffing, image extraction
│   └── vtex.py            # Valve texture/SVG decoding
├── api_gen/               # API generation from game data
│   ├── generator.py       # Main orchestrator (multi-language)
│   ├── loader.py          # Parses items_game.json, builds lookup tables
│   ├── state.py           # Central data store
│   ├── constants.py       # Image URL builder, rare-special tables, language list
│   ├── translations.py    # Multi-language translation system
│   ├── utils.py           # Weapon mappings, rarity colors, wear floats
│   └── items/             # 16 item generators (skins, stickers, crates, etc.)
├── storage.py             # Filesystem abstraction
└── static/                # Cached game data (translations, items_game, images.json)
```

## Requirements

- Python 3.10+
- A Steam account that owns CS2 (free)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/CS2Cap/CS2-API.git
   cd CS2-API
   ```

2. Install dependencies:

   ```bash
   pip install .
   ```

3. Create a `.env` file with your Steam credentials:

   ```env
   STEAM_USER=your_username
   STEAM_PASS=your_password
   SHARED_SECRET=your_2fa_shared_secret

   # Optional. Used as the base for image URLs the API generator embeds in
   # JSON output (e.g. https://cdn.example.com/images/<path>.png).
   # Defaults to https://cdn.cs2c.app
   IMAGE_BASE_URL=https://cdn.example.com
   ```

## Usage

**Track game files** (manifest, translations, items_game, images index):

```bash
python -m file_tracker.tracker
```

Add `--extract-images` to also download image shards and extract panorama PNGs/SVGs into `temp/images/`. This pulls a much larger set of VPK shards (tens of GB of temporary disk) and is left as an opt-in step:

```bash
python -m file_tracker.tracker --extract-images
```

Hosting the extracted images (e.g. uploading them to a CDN) is up to you. Whatever URL prefix you serve them from should match `IMAGE_BASE_URL`.

**Generate API** (per-language JSON files):

```bash
# English only (default)
python -m api_gen.generator

# Multiple languages by folder code
python -m api_gen.generator --languages en,fr,ru

# All 28 languages
python -m api_gen.generator --languages all
```

Pass `--force` to regenerate even when the manifest hasn't changed.

## Output

Per-language JSONs are written to `output/<lang>/`, one per item category:

| File | Description |
| ------ | ------------- |
| `agents.json` | Player character agents |
| `base_weapons.json` | Base weapon types |
| `skins.json` | Weapon skins grouped by paint kit |
| `skins_not_grouped.json` | Flat list of all weapon skins (per wear) |
| `stickers.json` | Stickers |
| `patches.json` | Patches |
| `graffiti.json` | Spray graffiti |
| `crates.json` | Weapon cases |
| `collections.json` | Weapon collections |
| `keys.json` | Case keys |
| `keychains.json` | Keychains |
| `music_kits.json` | Music kits |
| `collectibles.json` | Pins and collectibles |
| `sticker_slabs.json` | Sticker display cases |
| `highlights.json` | Highlight reels |
| `tools.json` | Tools |
| `inventory.json` | Combined inventory |
| `all.json` | All items in a flat dictionary keyed by id |

## Credits

This project is a Python rewrite of the original work by **[ByMykel](https://github.com/ByMykel)**:

- [CSGO-API](https://github.com/ByMykel/CSGO-API) — The original Node.js API generator for Counter-Strike 2 game items
- [counter-strike-file-tracker](https://github.com/ByMykel/counter-strike-file-tracker) — The original Node.js file tracker that monitors CS2 game files

## License

MIT

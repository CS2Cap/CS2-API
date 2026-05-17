"""Orchestrator: check manifest, download if changed, extract game files.

Image extraction is opt-in via ``--extract-images``. The image shards add
tens of gigabytes of temporary disk usage, so the default run only fetches
the small text shards needed for ``items_game.json`` and translations.
"""
import argparse
import os
import sys

import storage
from dotenv import load_dotenv

from file_tracker.steam_client import get_latest_manifest_id, login
from file_tracker.vpk_extractor import (
    cleanup,
    diff_image_crcs,
    download_vpk_files,
    extract_and_parse,
    extract_images,
    generate_default_generated,
    generate_images_json,
    get_image_crcs,
)

STATIC_DIR = "static"
TEMP_DIR = "temp"
IMAGES_DIR = os.path.join(TEMP_DIR, "images")
IMAGE_CRCS_PATH = os.path.join(STATIC_DIR, "image_crcs.json")


def run(extract_images_flag: bool = False) -> None:
    load_dotenv()

    username = os.getenv("STEAM_USER")
    password = os.getenv("STEAM_PASS")
    shared_secret = os.getenv("SHARED_SECRET")

    if not username or not password:
        print("STEAM_USER and STEAM_PASS must be set in .env")
        sys.exit(1)

    print("Getting latest manifest ID...")
    latest_manifest = get_latest_manifest_id()
    print(f"Latest manifest ID: {latest_manifest}")

    existing_manifest = storage.read(os.path.join(STATIC_DIR, "manifestId.txt"))
    if existing_manifest and existing_manifest.strip() == latest_manifest:
        print("Latest manifest matches existing, no update needed")
        return

    # An update is needed: log into the real account for depot downloads.
    print("Logging into Steam...")
    client = login(username, password, shared_secret)

    # Phase 1: Download pak01_dir.vpk and text-file shards (always needed)
    print("Manifest changed, downloading game files...")
    download_vpk_files(client, latest_manifest, TEMP_DIR, include_images=False)

    print("Extracting and parsing VPK text files...")
    extract_and_parse(TEMP_DIR, STATIC_DIR)

    # Phase 2: Build images index regardless (cheap, derived from VPK directory)
    base_url = os.getenv("IMAGE_BASE_URL", "https://cdn.cs2c.app").rstrip("/")
    images_json = generate_images_json(TEMP_DIR, base_url)
    storage.write_json(os.path.join(STATIC_DIR, "images.json"), images_json)

    default_gen = generate_default_generated(TEMP_DIR)
    storage.write_json(os.path.join(STATIC_DIR, "default_generated.json"), default_gen)

    # Phase 3 (opt-in): download image shards and extract PNGs/SVGs locally
    if extract_images_flag:
        old_crcs = storage.read_json(IMAGE_CRCS_PATH)
        new_crcs = get_image_crcs(TEMP_DIR)
        changed = diff_image_crcs(old_crcs, new_crcs)

        if changed:
            print(f"{len(changed)} images changed, downloading image shards...")
            download_vpk_files(
                client, latest_manifest, TEMP_DIR,
                include_images=True, changed_images=changed,
            )

            print(f"Extracting changed panorama images to {IMAGES_DIR}...")
            extract_images(TEMP_DIR, IMAGES_DIR, only_paths=changed)
            print(f"Done. Hosting/uploading the extracted images is up to you.")
        else:
            print("No image changes detected, skipping image extraction")

        storage.write_json(IMAGE_CRCS_PATH, new_crcs)
    else:
        print("Skipping image extraction (pass --extract-images to enable).")

    storage.write(os.path.join(STATIC_DIR, "manifestId.txt"), latest_manifest)

    print("Cleaning up temp files...")
    cleanup(TEMP_DIR)

    print("File tracker complete")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track CS2 game files via the Steam manifest.")
    parser.add_argument(
        "--extract-images",
        action="store_true",
        help=(
            "Also download image shards and extract panorama PNGs/SVGs to "
            f"{IMAGES_DIR}. Requires tens of GB of temporary disk space."
        ),
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    run(extract_images_flag=args.extract_images)

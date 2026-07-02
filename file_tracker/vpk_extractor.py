"""Download VPK archives from Steam CDN and extract game files to JSON."""
import json
import os
import shutil

import vdf
import vpk as vpk_lib
from steam.client import SteamClient
from steam.client.cdn import CDNClient

APP_ID = 730
DEPOT_ID = 2347770

_VPK_PATH_PREFIX = "game/csgo/"

_PANORAMA_PREFIX = "panorama/images/econ/"
_IMAGE_EXTENSIONS = (".vtex_c", ".vsvg_c")

VPK_FILES = [
    "resource/csgo_brazilian.txt",
    "resource/csgo_bulgarian.txt",
    "resource/csgo_czech.txt",
    "resource/csgo_danish.txt",
    "resource/csgo_dutch.txt",
    "resource/csgo_english.txt",
    "resource/csgo_finnish.txt",
    "resource/csgo_french.txt",
    "resource/csgo_german.txt",
    "resource/csgo_greek.txt",
    "resource/csgo_hungarian.txt",
    "resource/csgo_italian.txt",
    "resource/csgo_japanese.txt",
    "resource/csgo_koreana.txt",
    "resource/csgo_latam.txt",
    "resource/csgo_norwegian.txt",
    "resource/csgo_polish.txt",
    "resource/csgo_portuguese.txt",
    "resource/csgo_romanian.txt",
    "resource/csgo_russian.txt",
    "resource/csgo_schinese.txt",
    "resource/csgo_schinese_pw.txt",
    "resource/csgo_spanish.txt",
    "resource/csgo_swedish.txt",
    "resource/csgo_tchinese.txt",
    "resource/csgo_thai.txt",
    "resource/csgo_turkish.txt",
    "resource/csgo_ukrainian.txt",
    "resource/csgo_vietnamese.txt",
    "scripts/items/items_game.txt",
]


def _create_cdn_client(client: SteamClient) -> CDNClient:
    """Create CDNClient with an increased timeout for get_product_info."""
    import functools

    original = client.get_product_info
    client.get_product_info = functools.partial(original, timeout=30)
    try:
        cdn = CDNClient(client)
    finally:
        client.get_product_info = original
    return cdn


def get_image_crcs(temp_dir: str) -> dict[str, int]:
    """Read CRC32 for every panorama image in the VPK directory.

    Returns {vpk_path: crc32} for all panorama image files.
    """
    vpk_dir = vpk_lib.open(os.path.join(temp_dir, "pak01_dir.vpk"))
    crcs: dict[str, int] = {}
    for vpk_path in vpk_dir:
        if vpk_path.startswith(_PANORAMA_PREFIX) and vpk_path.endswith(
            _IMAGE_EXTENSIONS
        ):
            crcs[vpk_path] = vpk_dir.get_file_meta(vpk_path)["crc32"]
    return crcs


def diff_image_crcs(
    old_crcs: dict[str, int] | None, new_crcs: dict[str, int]
) -> set[str]:
    """Return the set of VPK paths that are new or changed."""
    if old_crcs is None:
        return set(new_crcs.keys())
    changed: set[str] = set()
    for path, crc in new_crcs.items():
        if path not in old_crcs or old_crcs[path] != crc:
            changed.add(path)
    return changed


def download_vpk_files(
    client: SteamClient,
    manifest_id: str,
    temp_dir: str,
    include_images: bool = False,
    changed_images: set[str] | None = None,
) -> None:
    """Download required VPK archives from Steam CDN to temp_dir."""
    os.makedirs(temp_dir, exist_ok=True)

    cdn = _create_cdn_client(client)

    manifest_request_code = cdn.get_manifest_request_code(APP_ID, DEPOT_ID, int(manifest_id))
    manifest = cdn.get_manifest(
        APP_ID,
        DEPOT_ID,
        int(manifest_id),
        manifest_request_code=manifest_request_code,
    )

    # Build a lookup: basename -> CDNDepotFile, but ONLY for files under game/csgo/.
    vpk_files_by_name: dict[str, object] = {}
    for depot_file in manifest.iter_files():
        if depot_file.is_directory:
            continue
        norm = depot_file.filename_raw.replace("\\", "/")
        if (
            norm.endswith(".vpk")
            and "pak01" in norm
            and norm.startswith(_VPK_PATH_PREFIX)
        ):
            basename = norm.split("/")[-1]
            vpk_files_by_name[basename] = depot_file

    # Download pak01_dir.vpk first so we can inspect which archive shards are needed
    dir_file = vpk_files_by_name.get("pak01_dir.vpk")
    if dir_file is None:
        raise RuntimeError("pak01_dir.vpk not found in manifest")

    dir_path = os.path.join(temp_dir, "pak01_dir.vpk")
    if not os.path.exists(dir_path):
        print("Downloading pak01_dir.vpk")
        _write_cdn_file(dir_file, dir_path)

    # Open the dir VPK to discover which archive indices hold our target files
    vpk_dir = vpk_lib.open(dir_path)
    required_indices: set[int] = set()
    for vpk_path in vpk_dir:
        for target in VPK_FILES:
            if vpk_path == target or vpk_path.startswith(target):
                required_indices.add(vpk_dir.get_file_meta(vpk_path)["archive_index"])
                break

    # Also collect shards for panorama images if requested
    if include_images:
        if changed_images is not None:
            # Incremental: only download shards for changed/new images
            for vpk_path in changed_images:
                try:
                    required_indices.add(
                        vpk_dir.get_file_meta(vpk_path)["archive_index"]
                    )
                except KeyError:
                    pass
            print(
                f"Incremental: {len(changed_images)} changed images "
                f"across {len(required_indices)} shards"
            )
        else:
            # Full: download all image shards
            image_count = 0
            for vpk_path in vpk_dir:
                if vpk_path.startswith(_PANORAMA_PREFIX) and vpk_path.endswith(
                    _IMAGE_EXTENSIONS
                ):
                    required_indices.add(
                        vpk_dir.get_file_meta(vpk_path)["archive_index"]
                    )
                    image_count += 1
            print(f"Found {image_count} panorama images across {len(required_indices)} shards")

    # Download only the archive shards we actually need (skip existing)
    for idx in sorted(required_indices):
        padded = str(idx).zfill(3)
        filename = f"pak01_{padded}.vpk"
        shard_path = os.path.join(temp_dir, filename)
        if os.path.exists(shard_path):
            continue
        shard_file = vpk_files_by_name.get(filename)
        if shard_file is None:
            raise RuntimeError(f"{filename} not found in manifest")
        print(f"Downloading {filename}")
        _write_cdn_file(shard_file, shard_path)


def _write_cdn_file(cdn_file, output_path: str) -> None:
    """Write the full content of a CDNDepotFile to disk."""
    cdn_file.seek(0)
    data = cdn_file.read()
    with open(output_path, "wb") as f:
        f.write(data)


def extract_and_parse(temp_dir: str, output_dir: str) -> None:
    """Extract target files from VPK, parse VDF to JSON, write to output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    vpk_dir = vpk_lib.open(os.path.join(temp_dir, "pak01_dir.vpk"))

    for target_file in VPK_FILES:
        found = False
        for vpk_path in vpk_dir:
            if vpk_path == target_file or vpk_path.startswith(target_file):
                file_data = vpk_dir[vpk_path].read()
                file_data = _trim_bom(file_data)
                file_str = file_data.decode("utf-8")
                parsed = vdf.loads(file_str)

                parts = target_file.split("/")
                out_name = parts[-1].replace(".txt", ".json")
                out_path = os.path.join(output_dir, out_name)

                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=4, ensure_ascii=False)

                print(f"Extracted {out_name}")
                found = True
                break

        if not found:
            raise RuntimeError(f"Could not find {target_file} in VPK")


def cleanup(temp_dir: str) -> None:
    """Remove temporary VPK files."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def extract_images(
    temp_dir: str, output_dir: str, only_paths: set[str] | None = None
) -> list[str]:
    """Extract and decode panorama images from VPK to output_dir.

    Decodes vtex_c → PNG and vsvg_c → SVG.
    Returns list of relative output paths (e.g. "econ/characters/foo_png.png").
    """
    from file_tracker.vtex import decode_vsvg, decode_vtex

    os.makedirs(output_dir, exist_ok=True)
    vpk_dir = vpk_lib.open(os.path.join(temp_dir, "pak01_dir.vpk"))
    extracted: list[str] = []
    errors = 0

    for vpk_path in vpk_dir:
        if not vpk_path.startswith(_PANORAMA_PREFIX):
            continue
        if not vpk_path.endswith(_IMAGE_EXTENSIONS):
            continue
        if only_paths is not None and vpk_path not in only_paths:
            continue

        try:
            raw = vpk_dir[vpk_path].read()
        except FileNotFoundError:
            continue

        # Decode compiled texture/svg → raw image bytes
        try:
            if vpk_path.endswith(".vtex_c"):
                ext, img_data = decode_vtex(raw)
                # Replace _png.vtex_c → _png.png (keep original naming)
                relative = vpk_path[len("panorama/images/"):]
                relative = relative.replace(".vtex_c", ext)
            else:
                ext, img_data = decode_vsvg(raw)
                relative = vpk_path[len("panorama/images/"):]
                relative = relative.replace(".vsvg_c", ext)
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Warning: failed to decode {vpk_path}: {e}")
            continue

        out_path = os.path.join(output_dir, relative.replace("/", os.sep))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(img_data)

        extracted.append(relative)

    print(f"Extracted {len(extracted)} panorama images ({errors} failures)")
    return extracted


def generate_images_json(temp_dir: str, base_url: str) -> dict[str, str]:
    """Generate images.json: maps image basenames to our CDN URLs."""
    vpk_dir = vpk_lib.open(os.path.join(temp_dir, "pak01_dir.vpk"))
    images: dict[str, str] = {}

    for vpk_path in vpk_dir:
        if not vpk_path.startswith(_PANORAMA_PREFIX):
            continue

        # Map compiled VPK path to output filename
        relative = vpk_path[len("panorama/images/"):]
        if relative.endswith("_png.vtex_c"):
            out_name = relative.replace(".vtex_c", ".png")
            key = relative[: -len("_png.vtex_c")]
        elif relative.endswith(".vtex_c"):
            out_name = relative.replace(".vtex_c", ".png")
            key = relative[: -len(".vtex_c")]
        elif relative.endswith(".vsvg_c"):
            out_name = relative.replace(".vsvg_c", ".svg")
            key = relative[: -len(".vsvg_c")]
        else:
            continue

        # Use only the basename as key
        key = key.rsplit("/", 1)[-1].lower()

        # Prefer PNG over SVG
        if key in images and out_name.endswith(".svg"):
            continue

        images[key] = f"{base_url}/images/{out_name}"

    print(f"Generated images.json with {len(images)} entries")
    return images


def generate_default_generated(temp_dir: str) -> list[str]:
    """Generate default_generated.json from VPK file listing.

    Returns list of filenames like "weapon_ak47_cu_ak47_anubis_light_png.png".
    """
    vpk_dir = vpk_lib.open(os.path.join(temp_dir, "pak01_dir.vpk"))
    result: list[str] = []

    prefix = "panorama/images/econ/default_generated/"
    for vpk_path in vpk_dir:
        if vpk_path.startswith(prefix) and vpk_path.endswith("_png.vtex_c"):
            # Convert filename: foo_png.vtex_c -> foo_png.png
            filename = vpk_path[len(prefix):].replace(".vtex_c", ".png")
            result.append(filename)

    print(f"Generated default_generated.json with {len(result)} entries")
    return sorted(result)


def _trim_bom(data: bytes) -> bytes:
    """Strip UTF-8 BOM if present."""
    if data[:3] == b"\xef\xbb\xbf":
        return data[3:]
    return data

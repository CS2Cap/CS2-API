"""Decode Valve compiled textures (vtex_c) and SVGs (vsvg_c) from VPK.

Handles three texture formats found in CS2 panorama images:
  - Format 16 (PNG_RGBA8888): embedded PNG data after VRF header
  - Format 28 (BGRA8888): LZ4-compressed raw pixels, converted to PNG
  - Format 2 (DXT5/BC3): LZ4-compressed block-compressed data, decoded to PNG

Some DXT5 textures use YCoCg color space (detected via REDI block marker).

vsvg_c files contain raw SVG XML inside the DATA block.
"""
import struct
from io import BytesIO

import lz4.block
import numpy as np
import texture2ddecoder
from PIL import Image

# Texture format IDs (VTexFormat enum from ValveResourceFormat)
_FMT_DXT5 = 2
_FMT_PNG_RGBA8888 = 16
_FMT_PNG_DXT5 = 18
_FMT_BGRA8888 = 28

# VTexExtraData types (from ValveResourceFormat)
_EXTRA_METADATA = 3

# YCoCg marker string embedded in REDI block of compiled textures
_YCOCG_MARKER = b"YCoCg"


def _parse_vrf_data_block(raw: bytes) -> tuple[int, int]:
    """Return (offset, size) of the DATA block in a VRF file."""
    block_count = struct.unpack_from("<I", raw, 12)[0]
    pos = 16
    for _ in range(block_count):
        btype = raw[pos : pos + 4]
        boff_rel = struct.unpack_from("<I", raw, pos + 4)[0]
        bsize = struct.unpack_from("<I", raw, pos + 8)[0]
        abs_off = (pos + 4) + boff_rel
        if btype == b"DATA":
            return abs_off, bsize
        pos += 12
    raise ValueError("No DATA block found in VRF file")


def _parse_non_pow2_dims(
    raw: bytes, data_off: int, width: int, height: int
) -> tuple[int, int]:
    """Read non-power-of-2 dimensions from the METADATA extra data block.

    Some textures are padded to power-of-2 sizes (FillToPowerOfTwo).  The
    actual image dimensions are stored in a METADATA extra data entry.
    Returns (actual_width, actual_height), falling back to (width, height)
    if no valid non-pow2 dims are found.
    """
    extra_data_offset = struct.unpack_from("<I", raw, data_off + 32)[0]
    extra_data_count = struct.unpack_from("<I", raw, data_off + 36)[0]
    if extra_data_count == 0:
        return width, height

    # Entry headers start at: (data_off+40) + (extra_data_offset - 8)
    cursor = (data_off + 40) + (extra_data_offset - 8)
    for _ in range(extra_data_count):
        etype = struct.unpack_from("<I", raw, cursor)[0]
        eoffset_raw = struct.unpack_from("<I", raw, cursor + 4)[0]
        # Data position: cursor+12 (after header) + (eoffset_raw - 8)
        entry_data = cursor + 4 + eoffset_raw

        if etype == _EXTRA_METADATA:
            # Skip 2 bytes, then read non-pow2 width and height (u16 each)
            nw = struct.unpack_from("<H", raw, entry_data + 2)[0]
            nh = struct.unpack_from("<H", raw, entry_data + 4)[0]
            if nw > 0 and nh > 0 and width >= nw and height >= nh:
                return nw, nh

        cursor += 12

    return width, height


def _apply_ycocg(img: Image.Image) -> Image.Image:
    """Convert DXT5-YCoCg decoded RGBA image to proper RGB.

    In YCoCg DXT5, the channels after BC3 decode are:
      R=Co+128, G=Cg+128, B=scale, A=Y (luminance).
    Formula from ValveResourceFormat/TextureDecoders/Common.cs.
    """
    arr = np.array(img, dtype=np.float64)
    R, G, B, A = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

    scale = np.floor(B / 8.0) + 1.0
    co = np.trunc((R - 128.0) / scale)
    cg = np.trunc((G - 128.0) / scale)

    out = np.empty_like(arr, dtype=np.uint8)
    out[:, :, 0] = np.clip(A + co - cg, 0, 255)
    out[:, :, 1] = np.clip(A + cg, 0, 255)
    out[:, :, 2] = np.clip(A - co - cg, 0, 255)
    out[:, :, 3] = 255
    return Image.fromarray(out, "RGBA")


def decode_vtex(raw: bytes) -> tuple[str, bytes]:
    """Decode a vtex_c file to an image.

    Returns (extension, image_bytes) where extension is ".png".
    """
    data_off, data_size = _parse_vrf_data_block(raw)
    vrf_end = data_off + data_size

    width = struct.unpack_from("<H", raw, data_off + 20)[0]
    height = struct.unpack_from("<H", raw, data_off + 22)[0]
    fmt = raw[data_off + 26]
    mip_count = raw[data_off + 27]
    actual_w, actual_h = _parse_non_pow2_dims(raw, data_off, width, height)

    # --- Formats 16/18: embedded PNG ---
    if fmt in (_FMT_PNG_RGBA8888, _FMT_PNG_DXT5):
        trailing = raw[vrf_end:]
        png_start = trailing.find(b"\x89PNG")
        if png_start == -1:
            raise ValueError("PNG signature not found in vtex_c")
        png_data = trailing[png_start:]
        # Crop if the embedded PNG has padding (unlikely but possible)
        if (actual_w, actual_h) != (width, height):
            img = Image.open(BytesIO(png_data))
            if img.size != (actual_w, actual_h):
                img = img.crop((0, 0, actual_w, actual_h))
                buf = BytesIO()
                img.save(buf, format="PNG")
                png_data = buf.getvalue()
        return ".png", png_data

    # --- Compressed pixel formats ---
    # Read per-mip compressed sizes from the last N u32s of the DATA block
    comp_sizes = []
    for i in range(mip_count):
        off = vrf_end - (mip_count - i) * 4
        comp_sizes.append(struct.unpack_from("<I", raw, off)[0])

    trailing = raw[vrf_end:]

    # Decompress mips (stored smallest-first in the file)
    off = 0
    mip0_data = b""
    for i in range(mip_count - 1, -1, -1):
        mw = max(1, width >> i)
        mh = max(1, height >> i)

        if fmt == _FMT_BGRA8888:
            expected = mw * mh * 4
        elif fmt == _FMT_DXT5:
            expected = max(1, (mw + 3) // 4) * max(1, (mh + 3) // 4) * 16
        else:
            raise ValueError(f"Unsupported vtex_c format: {fmt}")

        chunk = trailing[off : off + comp_sizes[i]]
        if comp_sizes[i] == expected:
            # Already uncompressed
            decompressed = chunk
        else:
            decompressed = lz4.block.decompress(chunk, uncompressed_size=expected)
        off += comp_sizes[i]

        if i == 0:
            mip0_data = decompressed

    # Convert to RGBA PNG
    if fmt == _FMT_BGRA8888:
        img = Image.frombytes("RGBA", (width, height), mip0_data, "raw", "BGRA")
    elif fmt == _FMT_DXT5:
        decoded = texture2ddecoder.decode_bc3(mip0_data, width, height)
        img = Image.frombytes("RGBA", (width, height), decoded, "raw", "BGRA")
        if _YCOCG_MARKER in raw:
            img = _apply_ycocg(img)
    else:
        raise ValueError(f"Unsupported vtex_c format: {fmt}")

    # Crop to actual dimensions if texture was padded to power-of-2
    if (actual_w, actual_h) != (width, height):
        img = img.crop((0, 0, actual_w, actual_h))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return ".png", buf.getvalue()


def decode_vsvg(raw: bytes) -> tuple[str, bytes]:
    """Decode a vsvg_c file to SVG.

    Returns (".svg", svg_bytes).
    """
    data_off, data_size = _parse_vrf_data_block(raw)
    block_data = raw[data_off : data_off + data_size]

    for marker in (b"<?xml", b"<svg"):
        idx = block_data.find(marker)
        if idx != -1:
            return ".svg", block_data[idx:]

    raise ValueError("No SVG content found in vsvg_c file")

import pathlib

# Custom base64-like alphabet used by VoiSona Mobile to embed audio data.
# '.' -> 0, 'A'-'Z' -> 1-26, 'a'-'z' -> 27-52, '0'-'9' -> 53-62, '+' -> 63.
ALPHABET = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"
_TABLE = {char: index for index, char in enumerate(ALPHABET)}


def decode_audio_data(field: str) -> bytes:
    """Decode the `ModileAudioData` field into a FLAC stream.

    The field is `<declared size>.<encoded body>`, where the body is a
    6-bit-per-symbol packing written LSB-first (unlike standard base64).
    """
    size_text, _, body = field.partition(".")
    size = int(size_text)
    buffer, accumulator, bit_count = bytearray(), 0, 0
    for char in body:
        accumulator |= _TABLE[char] << bit_count
        bit_count += 6
        while bit_count >= 8:
            buffer.append(accumulator & 0xFF)
            accumulator >>= 8
            bit_count -= 8
    return bytes(buffer[:size])


def encode_audio_data(flac: bytes) -> str:
    """Encode a FLAC stream into the `ModileAudioData` field format."""
    chars, accumulator, bit_count = [], 0, 0
    for byte in flac:
        accumulator |= byte << bit_count
        bit_count += 8
        while bit_count >= 6:
            chars.append(ALPHABET[accumulator & 0x3F])
            accumulator >>= 6
            bit_count -= 6
    if bit_count:
        chars.append(ALPHABET[accumulator & 0x3F])
    return f"{len(flac)}.{''.join(chars)}"


def extract_audio_files(
    path: pathlib.Path,
    audio_data: list[str],
    extract_audio: bool,
) -> list[pathlib.Path]:
    """Write embedded audio data next to the project file and return their paths.

    Paths are returned even when not written to disk, so that instrumental
    track import can still reference the expected location.
    """
    audio_paths = []
    for index, data in enumerate(audio_data, start=1):
        audio_path = path.parent / f"{path.stem}_{index}.flac"
        if extract_audio and not audio_path.exists():
            audio_path.write_bytes(decode_audio_data(data))
        audio_paths.append(audio_path)
    return audio_paths

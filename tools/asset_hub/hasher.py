"""Módulo de cálculo de firmas criptográficas (SHA-256) y hashes perceptuales (dHash)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pygame


def compute_sha256(file_path_or_bytes: Path | str | bytes) -> str:
    """Calcula el hash SHA-256 de un archivo en disco o de un búfer de bytes."""
    hasher = hashlib.sha256()
    if isinstance(file_path_or_bytes, (str, Path)):
        path = Path(file_path_or_bytes)
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
    elif isinstance(file_path_or_bytes, (bytes, bytearray)):
        hasher.update(file_path_or_bytes)
    else:
        raise TypeError(f"Tipo no soportado para hash: {type(file_path_or_bytes)}")
    return hasher.hexdigest()


def compute_dhash(surface: pygame.Surface, hash_size: int = 8) -> str:
    """Calcula el Difference Hash (dHash) de 64 bits de una superficie de Pygame.

    Escala la imagen a (hash_size + 1, hash_size), compara la luminancia horizontal
    y empaca los bits resultantes en una cadena hexadecimal de 16 caracteres.
    """
    scaled = pygame.transform.scale(surface, (hash_size + 1, hash_size))
    diff_bits: list[int] = []

    for y in range(hash_size):
        for x in range(hash_size):
            c1 = scaled.get_at((x, y))
            c2 = scaled.get_at((x + 1, y))
            # Coeficientes estándar de luminancia perceptiva (ITU-R BT.601)
            lum1 = c1[0] * 299 + c1[1] * 587 + c1[2] * 114
            lum2 = c2[0] * 299 + c2[1] * 587 + c2[2] * 114
            diff_bits.append(1 if lum2 > lum1 else 0)

    val = 0
    for bit in diff_bits:
        val = (val << 1) | bit

    return f"{val:016x}"


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calcula la distancia de Hamming entre dos hashes perceptuales en formato hexadecimal.

    Una distancia de 0 indica identidad perceptual absoluta.
    Una distancia <= 4 suele indicar duplicados con ligera compresión o escalado.
    """
    if len(hash1) != len(hash2):
        raise ValueError(f"Longitud de hashes incompatible: {len(hash1)} != {len(hash2)}")
    val1 = int(hash1, 16)
    val2 = int(hash2, 16)
    return bin(val1 ^ val2).count("1")

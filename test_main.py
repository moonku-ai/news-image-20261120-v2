"""Tests for news-image-20261120 v2 — 'THE WORLD ATLAS' (pure stdlib).

TDD: these tests were written BEFORE main.py. Run with:
    python3 -m unittest test_main -v
"""
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main


def parse_png_chunks(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG signature"
    pos = 8
    chunks = []
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        (crc,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        chunks.append((ctype, payload, crc))
        pos += 12 + length
    return chunks


class TestPngEncoding(unittest.TestCase):
    def test_png_signature_and_ihdr(self):
        data = main.render_png()
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        chunks = parse_png_chunks(data)
        self.assertEqual(chunks[0][0], b"IHDR")
        w, h, depth, ctype = struct.unpack(">IIBB", chunks[0][1][:10])
        self.assertEqual((w, h), (1024, 1024))
        self.assertEqual(depth, 8)
        self.assertEqual(ctype, 2)  # truecolour RGB
        self.assertEqual(chunks[-1][0], b"IEND")

    def test_png_chunk_crcs_valid(self):
        data = main.render_png()
        for ctype, payload, crc in parse_png_chunks(data):
            expect = zlib.crc32(ctype + payload) & 0xFFFFFFFF
            self.assertEqual(crc, expect, f"bad CRC on {ctype}")

    def test_png_decodes_to_full_frame(self):
        data = main.render_png()
        idat = b"".join(p for t, p, _ in parse_png_chunks(data) if t == b"IDAT")
        raw = zlib.decompress(idat)
        # filter byte per row + 1024 px * 3 bytes
        self.assertEqual(len(raw), 1024 * (1 + 1024 * 3))

    def test_size_under_1mib(self):
        data = main.render_png()
        self.assertLessEqual(len(data), 1048576, f"{len(data)} bytes > 1 MiB")

    def test_deterministic_two_runs(self):
        self.assertEqual(main.render_png(), main.render_png())


class TestFont(unittest.TestCase):
    def test_every_used_character_has_a_glyph(self):
        missing = sorted({ch for s in main.TEXT_STRINGS for ch in s if ch not in main.FONT})
        self.assertEqual(missing, [], f"missing glyphs: {missing}")

    def test_glyphs_are_7_rows_of_5_bits(self):
        for ch, rows in main.FONT.items():
            self.assertEqual(len(rows), 7, f"glyph {ch!r} must have 7 rows")
            for r in rows:
                self.assertGreaterEqual(r, 0)
                self.assertLess(r, 32, f"glyph {ch!r} row {r} exceeds 5 bits")

    def test_text_width_scales(self):
        w1 = main.text_width("ABC", 1)
        w2 = main.text_width("ABC", 2)
        self.assertEqual(w2, 2 * w1)

    def test_date_is_named(self):
        joined = " ".join(main.TEXT_STRINGS)
        self.assertIn("20 NOVEMBER 2026", joined)
        self.assertIn("FRIDAY", joined)


class TestLayout(unittest.TestCase):
    def test_wrap_fits_panel_widths(self):
        for text, scale, width in main.WRAP_CHECKS:
            lines = main.wrap_text(text, scale, width)
            for line in lines:
                self.assertLessEqual(
                    main.text_width(line, scale), width,
                    f"line {line!r} overflows width {width} at scale {scale}",
                )

    def test_wrap_never_drops_words(self):
        for text, scale, width in main.WRAP_CHECKS:
            lines = main.wrap_text(text, scale, width)
            self.assertEqual(" ".join(lines), " ".join(text.split()))

    def test_render_completes_without_out_of_bounds(self):
        # Canvas raises on any out-of-bounds write; render must not raise.
        data = main.render_png()
        self.assertGreater(len(data), 10000)

    def test_paper_is_not_mostly_blank(self):
        # Decode and count non-background pixels: the page must be drawn on.
        data = main.render_png()
        idat = b"".join(p for t, p, _ in parse_png_chunks(data) if t == b"IDAT")
        raw = zlib.decompress(idat)
        stride = 1 + 1024 * 3
        bg = bytes(main.PAPER)
        non_bg = 0
        for y in range(0, 1024, 4):
            row = raw[y * stride + 1:(y + 1) * stride]
            for x in range(0, 1024 * 3, 12):
                if row[x:x + 3] != bg:
                    non_bg += 1
        self.assertGreater(non_bg, 20000, "image looks mostly blank")


class TestMainEntry(unittest.TestCase):
    def test_main_writes_entry_png(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, MAKEFUN_OUTPUT_DIR=d)
            old = os.environ.get("MAKEFUN_OUTPUT_DIR")
            os.environ["MAKEFUN_OUTPUT_DIR"] = d
            try:
                main.main()
            finally:
                if old is None:
                    del os.environ["MAKEFUN_OUTPUT_DIR"]
                else:
                    os.environ["MAKEFUN_OUTPUT_DIR"] = old
            path = os.path.join(d, "entry.png")
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as f:
                self.assertTrue(f.read(8).startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()

# news-image-20261120-v2 — "THE WORLD ATLAS"

![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)
![status](https://img.shields.io/badge/status-v2%20iteration-orange)

Entry for the [make.fun](https://make.fun/bounty/news-image-20261120)
bounty **news-image-20261120** — "Sum up 20 November's world news in one
image". Prize $250 (top 50 paid, 1st $50). Entries close 22 Nov 2026 07:00
WIB; results due 6 Dec 2026 08:00 UTC.

## What it is

A light-paper **world atlas** of Friday 20 November 2026, drawn from scratch
in pure Python stdlib (no Pillow, no third-party deps). A stylised world map
carries numbered pins for the day's places; the lead story is the ICJ
genocide verdict, with the cyclone landfall, the Shenzhen trilateral summit
and the Seoul retrial below.

- **Lead — The Hague:** the ICJ finds Myanmar guilty of genocide against
  the Rohingya, 9–6 — the first time the court has found a *state* guilty
  of genocide. Verdict 19 Nov; the world reacts 20 Nov (UK expels Myanmar's
  defence attache, Switzerland expects compliance).
- **Odisha:** Cyclone Akvan comes ashore near Gopalpur at noon IST, 20 Nov —
  winds 90–100 km/h, 3 lakh evacuated, 423 rescue teams, 69 trains
  cancelled.
- **Shenzhen:** Trump, Xi and Putin hold their first trilateral meeting at
  APEC; their peace declaration says a nuclear war cannot be won and must
  never be fought — but sets no timelines and no Ukraine deal.
- **Seoul + markets:** South Korea's top court overturns ex-PM Han's
  15-year term and orders a retrial; Sensex +1.21%, Nifty +1.14%.
- **Also today:** APEC adopts the Shenzhen Outlook, the Nvidia CEO affair
  shadows APEC, Fiji's drought disaster, the Women's Asian Hockey Trophy
  opens, India v NZ Test goes on.

This is v2, an iteration of the accepted v1 entry (a dark "night desk"
storm chart led by the cyclone). v2 leads with the day's most consequential
story, uses fresher 20 Nov figures, covers more of the day, and uses a
lighter, higher-contrast paper palette.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png (1024x1024)
python3 -m unittest test_main -v         # 14 tests: PNG validity, size,
                                         # determinism, font coverage, layout
```

## Files

- `main.py` — the whole entry: 5x7 bitmap font, canvas, world map, PNG
  encoder (zlib + struct). Deterministic: two runs are byte-identical.
- `test_main.py` — test suite, written test-first.

## License

MIT — see `LICENSE`.

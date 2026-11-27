# Figure reproduction

Nine SVGs: score bounds, criterion bounds, and the distribution of all 1000 adverse margins, each in Russian, English and Simplified Chinese.

```sh
python render_figures.py
```

Run with Python 3.12, matplotlib and numpy. DejaVu Sans and Noto Serif CJK JP fonts were used. Font or library versions can change glyph paths and layout; the numerical evidence and seeded trial data are invariant. Matplotlib uses a fixed SVG hash salt and omits volatile date metadata.

The script reads `../releases/v2.0.0/RESULTS.json` and `data.json`; it does not change them. `chart-data.json` records plotted scores and the input SHA-256. `monte-carlo-margins.csv` retains all 1000 normalized weight vectors and adverse margins. No random changes to facts are made.

These figures describe public-documentation scores within a fixed candidate frame and weight sensitivity. They do not estimate trip-quality probabilities. Asterisks identify conditional eligibility; these candidates enter the adverse check at full upper bounds.

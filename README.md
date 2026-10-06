# Regular in what?

A short Quarto book on how "regular / rectilinear / curvilinear" gets
conflated with "longlat / projected" in gridded data, its concepts and its
software. It consolidates Michael Sumner's writing on the topic. First full
draft, 6 Oct 2026.

Rendered book: https://hypertidy.github.io/regular-in-what/

Build: `quarto render` (HTML into `_book/`). Pushes to `main` are rendered
and published to GitHub Pages by `.github/workflows/publish.yml`. Code chunks are not executed.
Figures: `python3 scripts/make_figures.py` (needs numpy, matplotlib,
pyproj) writes `figures/*.png` and prints the numbers quoted in the text.
Content is ASCII only.

## Stance

A grid is regular, rectilinear or curvilinear *in a frame*. "What kind of
grid?" is two questions (index mapping, and frame), plus a third thing
(what was stored) that conventions read as if it were the answer.

## Chapter to source map

| Chapter | Main sources (numbers refer to entries in the project source inventory) |
|---|---|
| Preface | scope note 6 Oct 2026; Grids post (2) |
| 1 One file, two grids | Coordinates broken in NetCDF (survey); Detecting hidden grids (3) |
| 2 Two questions | Grids post (2); CORDEX note (4); On dimension (1) |
| 3 Many costumes | rw-book grids.qmd A to H (6); a-book grid taxonomy (7); Degenerate rectilinear post; GHRSST chapter (6); GOES chat (5) |
| 4 Communities | raster-coordinate.md two worlds (survey, 7); xarray-r-design-analysis.md; Grids post (2); On dimension (1) |
| 5 Software | CORDEX note (4); gdal-hdf5-netcdf-remote.md; gdal-multidim-notes-2026-02-16.md; rrepr notes |
| 6 Field guide | Detecting hidden grids (3); CORDEX note (4); new simulation in scripts/ |
| 7 Cases | (3), (4), (5 chat-01, chat-03), (6), (7 OISST fragment) |
| 8 Edges | Grids post DGGS / L3bin sections (2); a-book CRS fragment (7); On dimension (1) |
| Appendices | CORDEX recipes (4); GHRSST fix (6); Grids post references (2) |

## Decisions taken in this draft

- Vocabulary: "regular in <frame>" everywhere; keep "degenerate
  rectilinear" and "cryptic curvilinear"; the rw-book term "degenerate
  curvilinear" is not used.
- A to H extended with E2 (regular in rotated longlat) and E3 (regular in
  scan angle, CRS not carried).
- Regular grid = six numbers (dimension + extent). The blog's "four
  numbers" means extent with dimension known; the book says six throughout.
  So the CryoSat ratio is quoted as about 35,000:1 (209,824 / 6), not the
  post's 52,000:1 (which divides by 4).
- ORCA described as tripolar, never rotated pole.

## To check before publishing

- OISST equal-area mean: "matched exactly" after a warp. Rerun, state the
  observed tolerance, publish the code (ch 7).
- ORCA northern pole locations: the Grids post says Greenland and Siberia;
  the book says North America and Asia (Madec and Imbard's ORCA design puts
  them in Canada and Siberia, from memory). Confirm.
- GDAL behaviours (ch 5) were observed on 2026 versions; recheck the
  classic netCDF axis-name check, the `rlon` warning, and whether
  `IsRegularlySpaced()` / `GuessGeoTransform()` are now in the C API.
- GHRSST longitude alignment: rw-book says "right-edge aligned"; confirm
  against a current file.
- Rotated-pole figure uses the EURO-CORDEX pole with an illustrative domain;
  swap for real RACMO ANT-12 parameters if wanted.
- CryoSat-2 real-file deviation (~70 m) vs simulated float32 (~1 m): the
  text suggests a different processing chain; confirm if it matters.

- L3bin section (ch 8): OBPG page text read via WebFetch on 6 Oct 2026
  (intermittently reachable; Michael uses the Wayback snapshot of 6 Jan 2026); PACE in the mission list comes from the Grids post,
  not that page. MODIS SIN tile numbers computed from R = 6371007.181 m;
  check the "tiles entirely off the Earth or ocean are not produced" wording.
  Possibly add: early MODIS land collections used an integerized
  sinusoidal (ISIN) grid before the SIN grid (from memory, unverified).

## Gaps (figures still wanted, need real data)

- ORCA Arctic nav_lon / nav_lat.
- VIIRS swath boundary, and the oblique Mercator strip.
- OISST three-ways result.
- CORDEX four-readers output, annotated.

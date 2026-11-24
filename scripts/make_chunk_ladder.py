"""Build the reference ladder figure (figures/chunk-ladder.svg).

Run from the book directory:  python3 scripts/make_chunk_ladder.py
Pure Python, no dependencies; writes SVG directly. What is known about an
array source, rung by rung; which rungs each format writes down; and views
alongside (chapter "One set of chunks, many containers").
"""
import os

W, H = 1400, 1020
FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"
INK, MUTED, RULE = "#1d2b36", "#5b6b78", "#c9d3db"
PANEL = "#f4f7f9"
ACCENT = "#2f6f9f"
EXPAND = "#b5562a"
LANE = {"cat": "#7a9cc0", "file": "#8aa67a", "manifest": "#c09a5a", "store": "#9a86b8", "table": "#2f6f9f"}
VIEW = "#6b7a86"

cols_x0, col_w, gap = 60, 285, 47
cx = [cols_x0 + i * (col_w + gap) for i in range(4)]
mid = [x + col_w / 2 for x in cx]
out = []

def text(x, y, s, size=15, fill=INK, weight="normal", anchor="start", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
               f'font-weight="{weight}" font-style="{style}" text-anchor="{anchor}">{s}</text>')

def rect(x, y, w, h, fill, stroke="none", sw=1, rx=0, dash=None, op=1):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
               f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def line(x1, y1, x2, y2, stroke=RULE, sw=1, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>')

# ---------------- A. the rungs ----------------
A_TOP, A_H = 30, 300
text(cols_x0, A_TOP + 4, "What is known about a source", 20, weight="bold")
rungs = [
    ("1  Reference", ["a URI, nothing more"]),
    ("2  Described container", ["shape, bounds, CRS, bands,", "data type: read once, cached"]),
    ("3  Indexed container", ["plus the internal chunk grid:", "offset and size of every chunk"]),
    ("4  Chunk rows", ["each chunk its own row,", "keyed by source and grid index"]),
]
py = A_TOP + 30
for i, (title, sub) in enumerate(rungs):
    x = cx[i]
    rect(x, py, col_w, A_H - 30, PANEL, RULE, 1, 8)
    text(x + 16, py + 30, title, 17, weight="bold")
    for k, s in enumerate(sub):
        text(x + 16, py + 54 + k * 19, s, 14, MUTED)

# pictograms (centred in each panel, from y = py + 105)
gy = py + 112
# 1: a file with a question mark
fx = mid[0] - 45
out.append(f'<path d="M {fx} {gy} h 66 l 24 24 v 106 h -90 Z" fill="white" stroke="{INK}" stroke-width="1.5"/>')
out.append(f'<path d="M {fx+66} {gy} v 24 h 24" fill="none" stroke="{INK}" stroke-width="1.5"/>')
text(mid[0], gy + 92, "?", 44, MUTED, "bold", "middle")
# 2: file with a label card (shape, bounds)
fx = mid[1] - 45
out.append(f'<path d="M {fx} {gy} h 66 l 24 24 v 106 h -90 Z" fill="white" stroke="{INK}" stroke-width="1.5"/>')
out.append(f'<path d="M {fx+66} {gy} v 24 h 24" fill="none" stroke="{INK}" stroke-width="1.5"/>')
rect(fx + 12, gy + 40, 66, 50, "#e3edf5", ACCENT, 1, 3)
for k, s in enumerate(["shape", "bounds", "crs"]):
    text(fx + 45, gy + 56 + k * 14, s, 11, ACCENT, anchor="middle")
# 3: file with an internal grid
fx = mid[2] - 45
out.append(f'<path d="M {fx} {gy} h 66 l 24 24 v 106 h -90 Z" fill="white" stroke="{INK}" stroke-width="1.5"/>')
out.append(f'<path d="M {fx+66} {gy} v 24 h 24" fill="none" stroke="{INK}" stroke-width="1.5"/>')
gx0, gy0, cs = fx + 12, gy + 36, 22
for r in range(4):
    for c in range(3):
        rect(gx0 + c * cs, gy0 + r * cs, cs, cs, "#e3edf5", ACCENT, 1)
# 4: chunk rows as a small table
tx, ty, tw, rh = mid[3] - 95, gy + 2, 190, 17
rect(tx, ty, tw, rh, "#d5e3ee", ACCENT, 1)
colx = [8, 48, 72, 132, 180]   # right edges for numbers, left for src
hdr = ["src", "i", "j", "offset", "size"]
rows = [["a", "0", "0", "512", "4096"], ["a", "0", "1", "4608", "4011"], ["a", "1", "0", "8619", "3987"],
        ["a", "1", "1", "12606", "4100"], ["b", "0", "0", "512", "3870"], ["...", "", "", "", ""]]
def trow(y, cells, weight="normal"):
    for c, v in enumerate(cells):
        if c == 0:
            text(tx + colx[0], y, v, 11, INK, weight)
        else:
            text(tx + colx[c], y, v, 11, INK, weight, "end")
trow(ty + 12.5, hdr, "bold")
for k, cells in enumerate(rows):
    rect(tx, ty + (k + 1) * rh, tw, rh, "white", RULE, 1)
    trow(ty + (k + 1) * rh + 12.5, cells)

# expand arrows between panels
labels = [("describe", "read the header, harvest", "a catalogue"),
          ("index", "GetRawBlockInfo(),", "TIFF tile offsets"),
          ("split", "one row per chunk", "")]
ay = py + 150
for i in range(3):
    x1, x2 = cx[i] + col_w + 4, cx[i + 1] - 4
    line(x1, ay, x2, ay, EXPAND, 2.5, marker="arr")
for i, (a, b, c) in enumerate(labels):
    xm = (cx[i] + col_w + cx[i + 1]) / 2
    text(xm, ay - 12, a, 14, EXPAND, "bold", "middle")
text(cols_x0, A_TOP + A_H + 26, "Moving right is always the same operation: expanding a reference into more specific references. "
     "Nothing about the bytes changes.", 14, MUTED, style="italic")

# ---------------- B. formats against the rungs ----------------
B_TOP = 400
text(cols_x0, B_TOP, "Which rungs each format writes down", 20, weight="bold")
for i in range(4):
    line(mid[i], B_TOP + 30, mid[i], B_TOP + 400, RULE, 1, "3,4")
    out.append(f'<circle cx="{mid[i]:.1f}" cy="{B_TOP + 18:.1f}" r="11" fill="white" stroke="{MUTED}" stroke-width="1.2"/>')
    text(mid[i], B_TOP + 22.5, str(i + 1), 13, MUTED, "bold", "middle")
lanes = [
    ("STAC item / asset", "cat", 0, 1, ("link", 2), "catalogue: a URI plus cached facts; an asset can link to a refs file"),
    ("COG, GeoTIFF", "file", 1, 2, None, "a self-describing file: header and tile offsets inside it"),
    ("netCDF / HDF5", "file", 1, 2, None, "the same, with the chunk index behind a B-tree"),
    ("Kerchunk, VirtualiZarr manifest", "manifest", 2, 3, None, "the chunk index pulled out of the file"),
    ("Icechunk", "manifest", 2, 3, None, "the same, versioned, with transactions"),
    ("Zarr v3 store", "store", 1, 3, ("split",), "zarr.json describes; each chunk is an object key, so the key is the index"),
    ("byterefs tables", "table", 1, 3, None, "sources table (rung 2) and chunk rows (rung 4) as plain tables"),
]
ly = B_TOP + 58
lh = 46
for k, (name, kind, a, b, reach, note) in enumerate(lanes):
    y = ly + k * lh
    out.append(f'<text x="{cols_x0 - 2}" y="{y - 6}" font-family="{FONT}" font-size="14">'
               f'<tspan fill="{INK}" font-weight="bold">{name}</tspan>'
               f'<tspan fill="{MUTED}" font-size="12.5" dx="12">{note}</tspan></text>')
    if reach is not None and reach[0] == "split":
        # two narrow pills, at the describe rung and the chunk rung, with no index between
        for r in (a, b):
            rect(mid[r] - 40, y, 80, 16, LANE[kind], rx=8)
        line(mid[a] + 40, y + 8, mid[b] - 40, y + 8, LANE[kind], 1.5, "2,5")
        rect(mid[2] - 52, y, 104, 16, "white")
        text(mid[2], y + 12, "no stored index", 11.5, LANE[kind], anchor="middle", style="italic")
        continue
    rect(mid[a] - 14, y, mid[b] - mid[a] + 28, 16, LANE[kind], rx=8)
    if reach is not None and reach[0] == "link":
        line(mid[b] + 14, y + 8, mid[reach[1]] - 6, y + 8, LANE[kind], 2, "2,4")
        out.append(f'<circle cx="{mid[reach[1]]:.1f}" cy="{y + 8:.1f}" r="6" fill="white" stroke="{LANE[kind]}" stroke-width="2"/>')
        text(mid[reach[1]] + 12, y + 12, "href", 11.5, LANE[kind], style="italic")
# views lane
vy = ly + len(lanes) * lh + 10
text(cols_x0 - 2, vy - 6, "Views: VRT, xarray Dataset, Zarr hierarchy, an engine's RASTER value", 14, INK, "bold")
rect(mid[0] - 14, vy, mid[3] - mid[0] + 28, 26, "white", VIEW, 2, 13, "6,4")
text((mid[0] + mid[3]) / 2, vy + 18, "a recipe for assembling pieces: can sit over any rung, including other views", 12.5, VIEW, anchor="middle")

# ---------------- C. dimensionality is a column count ----------------
C_TOP = 900
text(cols_x0, C_TOP, "At rung 4, dimensionality is just the number of index columns", 20, weight="bold")
def chunkrow(x, y, idx, vals, label):
    text(x, y - 8, label, 13, MUTED)
    cw = 58
    for k, h in enumerate(idx):
        rect(x + k * cw, y, cw, 20, "#e3edf5", ACCENT, 1)
        text(x + k * cw + cw / 2, y + 14, h, 12, ACCENT, "bold", "middle")
    x2 = x + len(idx) * cw + 8
    for k, h in enumerate(["uri", "offset", "size"]):
        rect(x2 + k * 70, y, 70, 20, "white", RULE, 1)
        text(x2 + k * 70 + 35, y + 14, h, 12, INK, anchor="middle")
chunkrow(cols_x0, C_TOP + 34, ["band", "row", "col"], [], "a COG tile")
chunkrow(cols_x0 + 640, C_TOP + 34, ["time", "depth", "y", "x"], [], "a netCDF chunk")
text(cols_x0, C_TOP + 88, "The 2D-raster versus multidimensional split lives in the view, where dimensions get meaning and coordinates.",
     14, MUTED, style="italic")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>One set of chunks, many containers</title>
<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
<path d="M 0 0 L 10 5 L 0 10 z" fill="{EXPAND}"/></marker></defs>
<rect width="{W}" height="{H}" fill="white"/>
{chr(10).join(out)}
</svg>
'''
OUT = os.path.join(os.path.dirname(__file__), "..", "figures", "chunk-ladder.svg")
open(OUT, "w").write(svg)
print("wrote chunk-ladder.svg")

"""Build the static figures for the book.

Run from the book directory:  python3 scripts/make_figures.py
Needs numpy, matplotlib, pyproj. Writes PNGs to figures/ and prints the
numbers quoted in the text. Every grid here is defined from its published
specification; nothing is read from data files.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import CRS, Transformer

OUT = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "figure.dpi": 110})
INK = "#1f3b57"
ACC = "#c0392b"


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight", dpi=130)
    plt.close(fig)
    print("wrote", name)


def lines_of(nx, ny, every):
    """Index-space polylines along rows and columns (cell centres)."""
    cols = [np.c_[np.full(ny, i), np.arange(ny)] for i in range(0, nx, every)]
    rows = [np.c_[np.arange(nx), np.full(nx, j)] for j in range(0, ny, every)]
    return cols + rows


def plot_lonlat_line(ax, lon, lat, **kw):
    """Break a polyline where it jumps across the antimeridian."""
    lon = np.asarray(lon, float)
    lat = np.asarray(lat, float)
    ok = np.isfinite(lon) & np.isfinite(lat)
    lon = np.where(ok, lon, np.nan)
    lat = np.where(ok, lat, np.nan)
    jump = np.r_[False, np.abs(np.diff(lon)) > 180]
    lon[jump] = np.nan
    ax.plot(lon, lat, **kw)


# ---------------------------------------------------------------------------
# 1. NSIDC 25 km south polar grid, EPSG:3412, in three frames
# ---------------------------------------------------------------------------
nx, ny, res = 316, 332, 25000.0
xmin, ymax = -3950000.0, 4350000.0
xc = xmin + (np.arange(nx) + 0.5) * res
yc = ymax - (np.arange(ny) + 0.5) * res
X, Y = np.meshgrid(xc, yc)

to_ll = Transformer.from_crs("EPSG:3412", "EPSG:4326", always_xy=True)
LON, LAT = to_ll.transform(X, Y)

fig, axs = plt.subplots(1, 2, figsize=(9, 4.2))
ax = axs[0]
for ln in lines_of(nx, ny, 12):
    i, j = ln[:, 0].astype(int), ln[:, 1].astype(int)
    ax.plot(X[j, i] / 1e3, Y[j, i] / 1e3, color=INK, lw=0.6)
ax.set_aspect("equal")
ax.set_title("(a) EPSG:3412: regular\n(six numbers + CRS)")
ax.set_xlabel("x (km)")
ax.set_ylabel("y (km)")
ax = axs[1]
for ln in lines_of(nx, ny, 12):
    i, j = ln[:, 0].astype(int), ln[:, 1].astype(int)
    plot_lonlat_line(ax, LON[j, i], LAT[j, i], color=INK, lw=0.6)
ax.set_title("(b) same cells, longitude/latitude:\nlooks curvilinear (2 x 104,912 values)")
ax.set_xlabel("longitude")
ax.set_ylabel("latitude")
ax.set_xlim(-180, 180)
ax.set_ylim(-90, -35)
save(fig, "nsidc-two-frames.png")

print("NSIDC lon range", LON.min(), LON.max(), " lat range", LAT.min(), LAT.max())


def regularity(x, y):
    """Max deviation from a regular grid, as a fraction of the median step."""
    dx = np.diff(x, axis=1)
    dy = np.diff(y, axis=0)
    mdx, mdy = np.median(dx), np.median(dy)
    row_y_sd = np.max(np.std(y, axis=1))
    col_x_sd = np.max(np.std(x, axis=0))
    return dict(dx=mdx, dy=mdy,
                dx_dev=np.max(np.abs(dx - mdx)), dy_dev=np.max(np.abs(dy - mdy)),
                row_y_sd=row_y_sd, col_x_sd=col_x_sd)


# Simulate the "cryptic curvilinear" file: store lon/lat as float32,
# then test regularity in candidate frames.
LON32 = LON.astype(np.float32).astype(float)
LAT32 = LAT.astype(np.float32).astype(float)
cands = {
    "EPSG:3412 (the true frame)": "EPSG:3412",
    "EPSG:3031 (WGS84, lat_ts -71)": "EPSG:3031",
    "LAEA south pole": "+proj=laea +lat_0=-90 +lon_0=0 +datum=WGS84",
}
print("\nRegularity of float32 lon/lat reprojected into candidate frames")
for name, crs in cands.items():
    t = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    px, py = t.transform(LON32, LAT32)
    r = regularity(px, py)
    print(f"  {name:32s} dx={r['dx']:.2f} max|dx-dx0|={r['dx_dev']:.3f} m "
          f"({100*r['dx_dev']/abs(r['dx']):.4f}%), max row-y sd={r['row_y_sd']:.3f} m")

# ---------------------------------------------------------------------------
# 2. Rotated pole: regular in rotated lon/lat, curvilinear in true lon/lat
#    Pole as used by EURO-CORDEX (grid_north_pole 39.25 N, 162 W);
#    the domain is illustrative, not a specific CORDEX grid.
# ---------------------------------------------------------------------------
rot = CRS("+proj=ob_tran +o_proj=longlat +o_lat_p=39.25 +o_lon_p=0 "
          "+lon_0=18 +datum=WGS84 +no_defs")
step = 0.44
rlon = np.arange(-28.0, 18.0 + 1e-9, step)
rlat = np.arange(-23.0, 21.5 + 1e-9, step)
RL, RT = np.meshgrid(rlon, rlat)
t_rot = Transformer.from_crs(rot, "EPSG:4326", always_xy=True)
GL, GT = t_rot.transform(RL, RT)
c_lon, c_lat = t_rot.transform(0.0, 0.0)
print(f"\nRotated grid {len(rlon)}x{len(rlat)}; rotated (0,0) -> lon {c_lon:.2f}, lat {c_lat:.2f}")
print(f"  true lon range {GL.min():.2f} {GL.max():.2f}; lat range {GT.min():.2f} {GT.max():.2f}")

fig, axs = plt.subplots(1, 2, figsize=(9, 4.0))
nrx, nry = len(rlon), len(rlat)
for ln in lines_of(nrx, nry, 8):
    i, j = ln[:, 0].astype(int), ln[:, 1].astype(int)
    axs[0].plot(RL[j, i], RT[j, i], color=INK, lw=0.6)
    axs[1].plot(GL[j, i], GT[j, i], color=INK, lw=0.6)
axs[0].set_aspect("equal")
axs[0].set_title("(a) rotated longitude/latitude:\nregular (0.44 deg steps)")
axs[0].set_xlabel("rlon (deg)")
axs[0].set_ylabel("rlat (deg)")
axs[1].set_aspect(1 / np.cos(np.deg2rad(50)))
axs[1].set_title("(b) true longitude/latitude:\ncurvilinear")
axs[1].set_xlabel("longitude")
axs[1].set_ylabel("latitude")
save(fig, "rotated-pole-two-frames.png")

# ---------------------------------------------------------------------------
# 3. Mercator grid stored as longitude/latitude (AVISO-style)
# ---------------------------------------------------------------------------
dlon = 1.0 / 3.0
nlat = 915
dy = np.deg2rad(dlon)                          # isotropic Mercator step
ymerc = (np.arange(nlat) - (nlat - 1) / 2) * dy
lat = np.rad2deg(np.arctan(np.sinh(ymerc)))
print(f"\nMercator-devolved: {nlat} rows, lat range {lat.min():.3f} {lat.max():.3f}; "
      f"lat step {np.diff(lat).min():.4f} to {np.diff(lat).max():.4f} deg")
yback = np.arcsinh(np.tan(np.deg2rad(lat)))
fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
axs[0].plot(lat[1:], np.diff(lat), color=INK)
axs[0].set_title("(a) step in latitude: varies\n(rectilinear in longitude/latitude)")
axs[0].set_xlabel("latitude")
axs[0].set_ylabel("delta latitude (deg)")
axs[1].plot(lat[1:], np.diff(yback), color=ACC)
axs[1].set_ylim(0, 2 * dy)
axs[1].set_title("(b) step in Mercator y: constant\n(regular in Mercator)")
axs[1].set_xlabel("latitude")
axs[1].set_ylabel("delta y (radians on unit sphere)")
save(fig, "mercator-devolved.png")
print("  Mercator y step deviation:", np.max(np.abs(np.diff(yback) - dy)))

# ---------------------------------------------------------------------------
# 4. Storage cost of one grid in three encodings
# ---------------------------------------------------------------------------
def cost(nx, ny):
    return [6, nx + ny, 2 * nx * ny]

grids = {"NSIDC 25 km\n316 x 332": (316, 332), "GOES ABI 2 km\n5424 x 5424": (5424, 5424)}
labels = ["affine\n(6 numbers)", "1D coords\n(nx + ny)", "2D coords\n(2 nx ny)"]
fig, axs = plt.subplots(1, 2, figsize=(9, 3.0), sharey=True)
for ax, (name, (gx, gy)) in zip(axs, grids.items()):
    c = cost(gx, gy)
    ax.bar(labels, c, color=[INK, "#5d7b99", ACC])
    ax.set_yscale("log")
    ax.set_title(name)
    for k, v in enumerate(c):
        ax.text(k, v * 1.3, f"{v:,}", ha="center")
    print(f"storage {name.splitlines()[0]}: {c}")
axs[0].set_ylabel("values stored (log scale)")
save(fig, "storage-cost.png")

# ---------------------------------------------------------------------------
# 5. Float32 coordinate noise (GHRSST MUR-style 0.01 deg longitude)
# ---------------------------------------------------------------------------
n = 36000
lon64 = -179.99 + np.arange(n) * 0.01
lon32 = lon64.astype(np.float32).astype(float)
d64, d32 = np.diff(lon64), np.diff(lon32)
print(f"\nfloat64 step range {d64.min():.16f} {d64.max():.16f}")
print(f"float32 step range {d32.min():.16f} {d32.max():.16f}")
fig, ax = plt.subplots(figsize=(9, 3.0))
ax.plot(lon32[1:], d32, ",", color=ACC, label="stored as float32")
ax.plot(lon64[1:], d64, ",", color=INK, label="computed in float64")
ax.set_xlabel("longitude")
ax.set_ylabel("step (deg)")
ax.set_title("A regular 0.01 deg axis: steps after storage as float32 vs float64")
ax.legend(markerscale=30, loc="lower left")
save(fig, "float32-steps.png")

# ---------------------------------------------------------------------------
# 6. Centres and edges
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5, 3.2))
ex, ey = np.arange(5), np.arange(4)
for v in ex:
    ax.plot([v, v], [0, 3], color=INK, lw=1)
for v in ey:
    ax.plot([0, 4], [v, v], color=INK, lw=1)
cx, cy = np.meshgrid(ex[:-1] + 0.5, ey[:-1] + 0.5)
ax.plot(cx, cy, "o", color=ACC, ms=5)
ax.set_xticks(ex)
ax.set_yticks(ey)
ax.set_aspect("equal")
ax.set_title("4 x 3 cells: 5 + 4 edge values, 4 + 3 centre values,\n"
             "or extent (0, 4, 0, 3) and dimension (4, 3)")
save(fig, "centre-edge.png")

# ---------------------------------------------------------------------------
# 7. GOES-16 ABI full disk fixed grid
# ---------------------------------------------------------------------------
h = 35786023.0
n = 5424
step = 56e-6
xr = (np.arange(n) - (n - 1) / 2) * step
print(f"\nGOES x[0:3] radians: {xr[:3]}")
geos = CRS(f"+proj=geos +h={h} +lon_0=-75 +sweep=x +ellps=GRS80 +units=m")
t_g = Transformer.from_crs(geos, "EPSG:4326", always_xy=True)
sub = np.arange(0, n, 8)
XR, YR = np.meshgrid(xr[sub], xr[sub][::-1])
GLON, GLAT = t_g.transform(XR * h, YR * h)
GLON = np.where(np.isfinite(GLON) & (np.abs(GLON) < 1e10), GLON, np.nan)
GLAT = np.where(np.isfinite(GLAT) & (np.abs(GLAT) < 1e10), GLAT, np.nan)
off = np.mean(np.isnan(GLON))
print(f"GOES off-disk fraction (subsampled): {off:.3f}")
fig, axs = plt.subplots(1, 2, figsize=(9, 4.2))
ns = len(sub)
for ln in lines_of(ns, ns, 40):
    i, j = ln[:, 0].astype(int), ln[:, 1].astype(int)
    axs[0].plot(XR[j, i], YR[j, i], color=INK, lw=0.6)
    plot_lonlat_line(axs[1], GLON[j, i], GLAT[j, i], color=INK, lw=0.6)
axs[0].set_aspect("equal")
axs[0].set_title("(a) scan angle (radians): regular\n(x times h gives metres in +proj=geos)")
axs[0].set_xlabel("x (rad)")
axs[0].set_ylabel("y (rad)")
axs[1].set_aspect("equal")
axs[1].set_title(f"(b) longitude/latitude: curvilinear,\n{100*off:.0f}% of cells off the Earth")
axs[1].set_xlabel("longitude")
axs[1].set_ylabel("latitude")
save(fig, "goes-two-frames.png")

# ---------------------------------------------------------------------------
# 8. L3bin integerized sinusoidal bins vs a regular sinusoidal grid
#    Scheme as published by NASA OBPG (Campbell et al. 1995), as implemented
#    in hypertidy/L3bin: numbin = int(2 * NUMROWS * cos(latbin) + 0.5)
# ---------------------------------------------------------------------------
def l3bin(nrows):
    latbin = (np.arange(nrows) + 0.5) * 180.0 / nrows - 90.0
    numbin = np.trunc(2 * nrows * np.cos(np.deg2rad(latbin)) + 0.5).astype(int)
    return latbin, numbin

for N in (180, 2160, 4320):
    print(f"L3bin NUMROWS={N}: total bins {l3bin(N)[1].sum():,}")

N = 18
latbin, numbin = l3bin(N)
edges = np.linspace(-90, 90, N + 1)
from matplotlib.patches import Rectangle, Polygon
fig, axs = plt.subplots(1, 3, figsize=(11, 3.4), gridspec_kw={"wspace": 0.4})
# (a) regular sinusoidal grid: cells off the Earth shaded
ax = axs[0]
nxs, nys = 2 * N, N
xe = np.linspace(-180, 180, nxs + 1)
off = 0
for j in range(nys):
    lat0, lat1 = edges[j], edges[j + 1]
    for i in range(nxs):
        x0, x1 = xe[i], xe[i + 1]
        # cell centre in sinusoidal x (degrees-equivalent); inside if |x| <= 180 cos(lat)
        xc_, yc_ = (x0 + x1) / 2, (lat0 + lat1) / 2
        inside = abs(xc_) <= 180 * np.cos(np.deg2rad(yc_))
        off += not inside
        ax.add_patch(Rectangle((x0, lat0), x1 - x0, lat1 - lat0,
                               facecolor=("none" if inside else "#e8c7b8"),
                               edgecolor=INK, lw=0.4))
yy = np.linspace(-90, 90, 200)
ax.plot(180 * np.cos(np.deg2rad(yy)), yy, color=ACC, lw=1.2)
ax.plot(-180 * np.cos(np.deg2rad(yy)), yy, color=ACC, lw=1.2)
ax.set_xlim(-185, 185); ax.set_ylim(-92, 92); ax.set_aspect("equal")
ax.set_title(f"(a) regular grid in sinusoidal:\n{off} of {nxs*nys} cells off the Earth")
ax.set_xlabel("sinusoidal x (deg at equator)")
print(f"regular sinusoidal {nxs}x{nys}: {off} cells off-Earth ({off/(nxs*nys):.2f}); "
      f"limit 1 - 2/pi = {1-2/np.pi:.3f}")
# (b) L3bin bins in sinusoidal
ax = axs[1]
for j in range(N):
    lat0, lat1 = edges[j], edges[j + 1]
    w = 360.0 / numbin[j]
    c = np.cos(np.deg2rad(latbin[j]))
    for k in range(numbin[j]):
        x0 = (-180 + k * w) * c
        ax.add_patch(Rectangle((x0, lat0), w * c, lat1 - lat0,
                               facecolor="none", edgecolor=INK, lw=0.4))
ax.plot(180 * np.cos(np.deg2rad(yy)), yy, color=ACC, lw=1.2)
ax.plot(-180 * np.cos(np.deg2rad(yy)), yy, color=ACC, lw=1.2)
ax.set_xlim(-185, 185); ax.set_ylim(-92, 92); ax.set_aspect("equal")
ax.set_title(f"(b) L3 bins, NUMROWS = {N}:\nrows of {numbin.min()} to {numbin.max()} bins")
ax.set_xlabel("sinusoidal x (deg at equator)")
# (c) the ragged array: bins per row
ax = axs[2]
ax.barh(latbin, numbin, height=180 / N * 0.85, color=INK)
ax.set_xlabel("bins in row")
ax.set_ylabel("row centre latitude")
ax.set_title("(c) the ragged array:\none integer defines it all")
ax.set_ylim(-92, 92)
save(fig, "l3bin.png")

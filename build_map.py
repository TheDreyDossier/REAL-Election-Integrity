"""
Build a static US states SVG for the REAL Election Integrity site.
Reads us-atlas topojson, applies Albers-USA-like projection (with AK/HI repositioned),
and emits inline SVG paths with data-state attributes we can hover/click in the browser.
"""
import json
import math
from pathlib import Path

DOCS = Path(__file__).parent / "docs"
TOPO = DOCS / "data" / "us-states-topo.json"
OUT_SVG = DOCS / "assets" / "us-map.svg"

# US state FIPS -> slug (matches our /states/<slug>.html files)
FIPS_TO_SLUG = {
    "01": "alabama", "02": "alaska", "04": "arizona", "05": "arkansas",
    "06": "california", "08": "colorado", "09": "connecticut", "10": "delaware",
    "11": "district-of-columbia", "12": "florida", "13": "georgia", "15": "hawaii",
    "16": "idaho", "17": "illinois", "18": "indiana", "19": "iowa",
    "20": "kansas", "21": "kentucky", "22": "louisiana", "23": "maine",
    "24": "maryland", "25": "massachusetts", "26": "michigan", "27": "minnesota",
    "28": "mississippi", "29": "missouri", "30": "montana", "31": "nebraska",
    "32": "nevada", "33": "new-hampshire", "34": "new-jersey", "35": "new-mexico",
    "36": "new-york", "37": "north-carolina", "38": "north-dakota", "39": "ohio",
    "40": "oklahoma", "41": "oregon", "42": "pennsylvania", "44": "rhode-island",
    "45": "south-carolina", "46": "south-dakota", "47": "tennessee", "48": "texas",
    "49": "utah", "50": "vermont", "51": "virginia", "53": "washington",
    "54": "west-virginia", "55": "wisconsin", "56": "wyoming",
}
FIPS_TO_ABBR = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}
FIPS_TO_NAME = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "District of Columbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
    "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
    "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico",
    "36": "New York", "37": "North Carolina", "38": "North Dakota", "39": "Ohio",
    "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
    "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
    "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming",
}


def topo_to_geo(topo, layer):
    """Convert a topojson layer to plain geojson feature list."""
    arcs = topo["arcs"]
    tr = topo.get("transform")
    if tr:
        sx, sy = tr["scale"]
        tx, ty = tr["translate"]

    def dequantize(arc):
        pts = []
        x = y = 0
        for dx, dy in arc:
            x += dx
            y += dy
            if tr:
                pts.append([x * sx + tx, y * sy + ty])
            else:
                pts.append([x, y])
        return pts

    decoded_arcs = [dequantize(a) for a in arcs]

    def arc_to_coords(idx):
        if idx < 0:
            return list(reversed(decoded_arcs[~idx]))
        return decoded_arcs[idx]

    def ring(arc_ids):
        coords = []
        for i, aid in enumerate(arc_ids):
            piece = arc_to_coords(aid)
            if i > 0:
                piece = piece[1:]  # skip duplicate join point
            coords.extend(piece)
        return coords

    features = []
    for feat in topo["objects"][layer]["geometries"]:
        gtype = feat["type"]
        if gtype == "Polygon":
            coords = [ring(r) for r in feat["arcs"]]
        elif gtype == "MultiPolygon":
            coords = [[ring(r) for r in poly] for poly in feat["arcs"]]
        else:
            continue
        features.append({
            "id": feat["id"],
            "properties": feat.get("properties", {}),
            "geometry": {"type": gtype, "coordinates": coords},
        })
    return features


# --- Albers USA-ish projection ---
# Continental US: Albers with parallels 29.5, 45.5, center (-96, 37.5)
# Alaska + Hawaii: separately projected then translated to lower-left of frame.

def albers(lon, lat, lon0, lat0, phi1, phi2):
    lon_r, lat_r = math.radians(lon), math.radians(lat)
    lon0_r, lat0_r = math.radians(lon0), math.radians(lat0)
    phi1_r, phi2_r = math.radians(phi1), math.radians(phi2)
    n = 0.5 * (math.sin(phi1_r) + math.sin(phi2_r))
    C = math.cos(phi1_r) ** 2 + 2 * n * math.sin(phi1_r)
    rho0 = math.sqrt(C - 2 * n * math.sin(lat0_r)) / n
    rho = math.sqrt(C - 2 * n * math.sin(lat_r)) / n
    theta = n * (lon_r - lon0_r)
    x = rho * math.sin(theta)
    y = rho0 - rho * math.cos(theta)
    return x, y


def project_point(lon, lat, fips):
    """Return (x, y) in projected space. AK, HI, PR get their own projections + translation."""
    if fips == "02":  # Alaska
        # Rotate + shrink AK, translate to lower-left
        x, y = albers(lon, lat, -152, 60, 55, 65)
        return x * 0.35 - 0.30, y * 0.35 + 0.55
    if fips == "15":  # Hawaii
        x, y = albers(lon, lat, -157, 20, 8, 18)
        return x * 1.0 - 0.05, y * 1.0 + 0.60
    if fips == "72":  # Puerto Rico - skip
        return None
    # Continental US
    return albers(lon, lat, -96, 37.5, 29.5, 45.5)


def project_geometry(geom, fips):
    def project_ring(ring):
        out = []
        for lon, lat in ring:
            p = project_point(lon, lat, fips)
            if p is None:
                return None
            out.append(p)
        return out

    if geom["type"] == "Polygon":
        rings = [project_ring(r) for r in geom["coordinates"]]
        if any(r is None for r in rings):
            return None
        return {"type": "Polygon", "coordinates": rings}
    if geom["type"] == "MultiPolygon":
        polys = []
        for poly in geom["coordinates"]:
            rings = [project_ring(r) for r in poly]
            if any(r is None for r in rings):
                continue
            polys.append(rings)
        if not polys:
            return None
        return {"type": "MultiPolygon", "coordinates": polys}
    return None


def geometry_to_path(geom, sx, sy, tx, ty):
    """Convert projected geometry to an SVG path 'd' string."""
    parts = []

    def ring_to_str(ring):
        s = []
        for i, (x, y) in enumerate(ring):
            X = x * sx + tx
            Y = y * sy + ty
            s.append(f"{'M' if i == 0 else 'L'}{X:.1f},{Y:.1f}")
        s.append("Z")
        return "".join(s)

    if geom["type"] == "Polygon":
        for r in geom["coordinates"]:
            parts.append(ring_to_str(r))
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            for r in poly:
                parts.append(ring_to_str(r))
    return "".join(parts)


def compute_bounds(features):
    xs, ys = [], []
    for f in features:
        g = f["geometry"]
        rings = []
        if g["type"] == "Polygon":
            rings = g["coordinates"]
        else:
            for poly in g["coordinates"]:
                rings.extend(poly)
        for r in rings:
            for x, y in r:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def main():
    topo = json.loads(TOPO.read_text())
    features = topo_to_geo(topo, "states")
    print(f"  Loaded {len(features)} state features")

    # Project each
    proj_features = []
    for f in features:
        fips = f["id"]
        if fips not in FIPS_TO_SLUG:
            continue
        pg = project_geometry(f["geometry"], fips)
        if pg is None:
            continue
        proj_features.append({"id": fips, "geometry": pg})

    # Compute bounds and scale to viewBox 0 0 960 600
    W, H = 960, 600
    minx, miny, maxx, maxy = compute_bounds(proj_features)
    # y is inverted (up in projection = down in svg? no, both x/y increase; but latitude increases north, and albers y_out increases south (rho0 - rho*cos increases when lat decreases). Verify empirically.)
    px = maxx - minx
    py = maxy - miny
    scale = min(W / px, H / py) * 0.94
    tx = (W - scale * px) / 2 - scale * minx
    ty = (H - scale * py) / 2 - scale * miny

    # Build SVG
    svg_paths = []
    for pf in proj_features:
        fips = pf["id"]
        slug = FIPS_TO_SLUG[fips]
        abbr = FIPS_TO_ABBR[fips]
        name = FIPS_TO_NAME[fips]
        d = geometry_to_path(pf["geometry"], scale, scale, tx, ty)
        svg_paths.append(
            f'<path class="rei-map__state" data-state="{slug}" data-abbr="{abbr}" data-name="{name}" d="{d}"/>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'class="rei-map__svg" aria-label="United States \u2014 click a state to view its fact-check">\n'
        + "\n".join(svg_paths)
        + "\n</svg>\n"
    )
    OUT_SVG.write_text(svg)
    print(f"  Wrote {OUT_SVG} ({OUT_SVG.stat().st_size} bytes, {len(svg_paths)} states)")


if __name__ == "__main__":
    main()

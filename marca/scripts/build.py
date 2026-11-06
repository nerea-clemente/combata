import sys, os, re, json
import numpy as np, cv2, vtracer, cairosvg
from PIL import Image

W = os.path.dirname(os.path.abspath(__file__)) + "/work"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/out/Combata_Identidad_Visual_HQ"
S = 8  # upscale factor

PAL = {"N": (0x1A,0x0B,0x3D), "L": (0xD9,0xFF,0x00), "P": (0xFF,0x2E,0xA6),
       "V": (0xB6,0xA4,0xFF), "W": (0xFF,0xFF,0xFF)}
HEX = {k: "#%02X%02X%02X" % v for k, v in PAL.items()}
# reference values as they appear in the source image (to classify), mapped to brand colours
REFC = {"N": (0x1A,0x0B,0x3D), "L": (0xEE,0xFF,0x10), "P": (0xF0,0x5A,0xB0),
        "V": (0xB6,0xA4,0xFF), "W": (0xFF,0xFF,0xFF)}

# name: (colours, bg mode, sticker)
CFG = {
 "logo_combata_principal": ("NW", "all", False),
 "logo_combata_bubble": ("NLW", "all_but_inside", False),
 "isotipo_nube_vaso_gafas": ("NLVW", "flood", False),
 "isotipo_nube_vaso_sin_gafas": ("NLVW", "flood", False),
 "avatar_nube_gafas": ("NLVW", "flood", False),
 "avatar_nube_sin_gafas": ("NLVW", "flood", False),
 "nube_gafas": ("NLW", "flood", False),
 "nube_sonriente": ("NW", "flood", False),
 "nube_gafas_simple": ("NW", "flood", False),
 "nube_sonriente_simple": ("NW", "flood", False),
 "vaso": ("NVW", "flood", True),
 "corazon": ("NPW", "flood", True),
 "brillo": ("NLW", "flood", True),
 "onda": ("NVW", "flood", True),
 "rayos": ("NLW", "flood", True),
 "nube_amarilla": ("LW", "all", False),
 "nube_lila": ("VW", "all", False),
 "trazos": ("NW", "all", False),
 "subrayado": ("NLW", "all", False),
 "favicon_gafas": ("NLVW", "flood", False),
 "favicon_sin_gafas": ("NLVW", "flood", False),
}

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
_SORA = None
def reg_glyph(cx, cy, size, color):
    global _SORA
    if _SORA is None:
        f = TTFont(os.path.dirname(os.path.abspath(__file__)) + "/Sora.ttf")
        _SORA = instancer.instantiateVariableFont(f, {"wght": 700})
    gs = _SORA.getGlyphSet(); g = _SORA.getBestCmap()[ord("R")]
    bp = BoundsPen(gs); gs[g].draw(bp); xmin, ymin, xmax, ymax = bp.bounds
    pen = SVGPathPen(gs); gs[g].draw(pen)
    k = size * 0.95 / (ymax - ymin)
    tx = cx - (xmin + xmax) / 2 * k; ty = cy + (ymin + ymax) / 2 * k
    return f'<path transform="translate({tx:.2f} {ty:.2f}) scale({k:.5f} {-k:.5f})" d="{pen.getCommands()}" fill="{color}"/>'

def tm_glyph(left, top, height, color):
    reg_glyph(0, 0, 1, color)  # ensure font loaded
    gs = _SORA.getGlyphSet(); g = _SORA.getBestCmap()[0x2122]
    bp = BoundsPen(gs); gs[g].draw(bp); xmin, ymin, xmax, ymax = bp.bounds
    pen = SVGPathPen(gs); gs[g].draw(pen)
    k = height / (ymax - ymin)
    tx = left - xmin * k; ty = top + ymax * k
    return f'<path transform="translate({tx:.2f} {ty:.2f}) scale({k:.5f} {-k:.5f})" d="{pen.getCommands()}" fill="{color}"/>'

def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))

def process(name, folder):
    cols, bg, sticker = CFG[name]
    src = cv2.cvtColor(cv2.imread(f"{W}/crops/{name}.png"), cv2.COLOR_BGR2RGB)
    pad = 6 if sticker else 3
    src = cv2.copyMakeBorder(src, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
    h, w = src.shape[:2]
    big = cv2.resize(src, (w*S, h*S), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    big = cv2.GaussianBlur(big, (0, 0), S*0.35)
    lab_big = cv2.cvtColor(np.clip(big, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    keys = list(cols)
    P = np.array([REFC[k] for k in keys], np.float32)
    px = big.reshape(-1, 3)
    best_d = np.full(px.shape[0], np.inf, np.float32); best_l = np.zeros(px.shape[0], np.int32)
    # model each pixel as a mix of two allowed colours (anti-aliasing / blur); pick nearest segment
    for i in range(len(keys)):
        for j in range(i, len(keys)):
            a, b = P[i], P[j]
            ab = b - a; L2 = float((ab*ab).sum())
            t = np.zeros(px.shape[0], np.float32) if L2 == 0 else np.clip(((px - a) @ ab) / L2, 0, 1)
            proj = a + t[:, None] * ab
            dd = ((px - proj) ** 2).sum(1)
            # small penalty so pure colours prefer their own label over mixes
            dd = dd + (0 if i == j else 40.0)
            lbl = np.where(t < 0.5, i, j)
            upd = dd < best_d
            best_d[upd] = dd[upd]; best_l[upd] = lbl[upd]
    lab = best_l.reshape(big.shape[:2])
    def fill_unassigned(lab):
        un = lab < 0
        if un.any():
            mask = (~un).astype(np.uint8)
            _, idx = cv2.distanceTransformWithLabels(1 - mask, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
            ys, xs = np.nonzero(mask)
            lut = lab[ys, xs]
            lab = np.where(un, lut[idx - 1], lab)
        return lab
    lab = fill_unassigned(lab)
    # background -> transparent (label T = len(keys))
    T = len(keys)
    wi = keys.index("W")
    white = (lab == wi).astype(np.uint8)
    if bg == "all":
        lab[white == 1] = T
    else:
        n, cc = cv2.connectedComponents(white, connectivity=4)
        border = set(np.unique(np.concatenate([cc[0], cc[-1], cc[:, 0], cc[:, -1]]))) - {0}
        bgmask = np.isin(cc, list(border))
        if bg == "all_but_inside":  # logo bubble: counters inside letters also transparent? keep: make all white transparent
            bgmask = white == 1
        lab[bgmask] = T
    if name.startswith(("avatar", "favicon")):
        bgk = keys.index("N") if "gafas" in name and "sin" not in name else keys.index("L")
        ys, xs = np.nonzero(lab != T)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        side = min(y1 - y0, x1 - x0)
        r = int(side * 0.21)
        rr = np.zeros(lab.shape, np.uint8)
        cv2.rectangle(rr, (x0 + r, y0), (x1 - r, y1), 1, -1)
        cv2.rectangle(rr, (x0, y0 + r), (x1, y1 - r), 1, -1)
        for cx, cy in ((x0+r, y0+r), (x1-r, y0+r), (x0+r, y1-r), (x1-r, y1-r)):
            cv2.circle(rr, (cx, cy), r, 1, -1, lineType=cv2.LINE_8)
        lab[rr == 0] = T
        lab[(rr == 1) & (lab == T)] = bgk
        # thin rim of misclassified pixels near the edge -> background colour
        inner = cv2.erode(rr, disk(S*2.5))
        rim = (rr == 1) & (inner == 0)
        lab[rim] = bgk
    reg = None
    if name.startswith("logo"):
        ni = keys.index("N")
        nm = (lab == ni).astype(np.uint8)
        n, cc, st, cen = cv2.connectedComponentsWithStats(nm, connectivity=8)
        H = nm.shape[0]
        big_h = st[1:, cv2.CC_STAT_HEIGHT].max()
        small = [i for i in range(1, n) if st[i, cv2.CC_STAT_HEIGHT] < big_h * 0.4]
        # the registered mark = small comps in the right-most 8% of the width
        xmax = max(st[i, 0] + st[i, 2] for i in range(1, n))
        small = [i for i in small if st[i, 0] > xmax - big_h * 0.45]
        if small:
            x0 = min(st[i, 0] for i in small); y0 = min(st[i, 1] for i in small)
            x1 = max(st[i, 0] + st[i, 2] for i in small); y1 = max(st[i, 1] + st[i, 3] for i in small)
            reg = ((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2)
            fillk = keys.index("L") if "L" in keys else T
            box = np.zeros_like(nm); cv2.circle(box, (int(reg[0]), int(reg[1])), int(reg[2] * 1.15), 1, -1)
            lab[(box == 1) & (lab != T)] = fillk
            lab[(box == 1) & (lab == T) & (fillk != T)] = fillk if "bubble" not in name else lab[(box == 1) & (lab == T)]
    if name == "logo_combata_bubble":
        sil = (lab != T).astype(np.float32)
        sil = cv2.morphologyEx(sil, cv2.MORPH_CLOSE, disk(S*2))
        sil_s = cv2.GaussianBlur(sil, (0, 0), S*2.2) > 0.5
        lab[sil_s & (lab == T)] = keys.index("L")
        lab[~sil_s] = T
    keys2 = keys + ["T"]
    # smooth contours: soft majority vote
    K = len(keys2)
    stack = np.stack([cv2.GaussianBlur((lab == k).astype(np.float32), (0, 0), S*(0.8 if name.startswith('logo') else 0.45)) for k in range(K)])
    lab = stack.argmax(0)
    # small speckles: remove components < area
    minA = (S*1.5) ** 2
    for k in range(K):
        m = (lab == k).astype(np.uint8)
        n, cc, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] < minA:
                lab[cc == i] = -1
    lab = fill_unassigned(lab)
    rgba = np.zeros(lab.shape + (4,), np.uint8)
    for k, key in enumerate(keys):
        rgba[lab == k] = PAL[key] + (255,)
    if sticker:
        fg = (lab != T).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, disk(S*3))
        border = cv2.dilate(fg, disk(S*4.2))
        border = cv2.GaussianBlur(border.astype(np.float32), (0, 0), S*1.2) > 0.5
        outline = cv2.dilate(border.astype(np.uint8), disk(S*0.7)) > 0
        newa = np.zeros_like(rgba)
        newa[outline] = (0xE2, 0xDD, 0xF0, 255)
        newa[border] = (255, 255, 255, 255)
        keep = rgba[:, :, 3] > 0
        newa[keep] = rgba[keep]
        rgba = newa
    # crop to content with margin
    ys, xs = np.nonzero(rgba[:, :, 3])
    if reg is not None:
        ys = np.append(ys, [int(reg[1] - reg[2]), int(reg[1] + reg[2])]); xs = np.append(xs, [int(reg[0] - reg[2]), int(reg[0] + reg[2] * 1.4)])
    m = S * 2
    y0, y1 = max(ys.min() - m, 0), min(ys.max() + m, rgba.shape[0])
    x0, x1 = max(xs.min() - m, 0), min(xs.max() + m, rgba.shape[1])
    rgba = rgba[y0:y1, x0:x1]
    x0c, y0c = x0, y0
    tmp = f"{W}/tmp_{name}.png"
    Image.fromarray(rgba, "RGBA").save(tmp)
    # per-colour layered tracing (bottom -> top); each layer extends slightly under its upper neighbours
    rgb = rgba[:, :, :3].astype(np.int32); al = rgba[:, :, 3]
    code = (rgb[:, :, 0] << 16) | (rgb[:, :, 1] << 8) | rgb[:, :, 2]
    order = ["#E2DDF0", HEX["W"], HEX["V"], HEX["P"], HEX["L"], HEX["N"]]
    present = [hx for hx in order if ((code == int(hx[1:], 16)) & (al > 0)).any()]
    paths = []
    for li, hx in enumerate(present):
        m = (code == int(hx[1:], 16)) & (al > 0)
        upper = np.zeros_like(m)
        for hx2 in present[li+1:]:
            upper |= (code == int(hx2[1:], 16)) & (al > 0)
        ext = cv2.dilate(m.astype(np.uint8), disk(S*0.8)).astype(bool) & upper
        m = m | ext
        img = np.where(m, 0, 255).astype(np.uint8)
        mp = f"{W}/tmp_{name}_{li}.png"
        Image.fromarray(img, "L").save(mp)
        sp = mp[:-4] + ".svg"
        vtracer.convert_image_to_svg_py(mp, sp, colormode="binary", mode="spline",
            filter_speckle=int(S*1.5), corner_threshold=70, length_threshold=6.0,
            max_iterations=10, splice_threshold=45, path_precision=2)
        for p in re.findall(r'<path[^>]*/>', open(sp).read()):
            p = re.sub(r'fill="[^"]*"', f'fill="{hx}"', p)
            paths.append(p)
    if reg is not None:
        cx, cy, r = reg[0] - x0c, reg[1] - y0c, reg[2]
        paths.append(tm_glyph(cx - r * 0.95, cy - r * 0.95, r * 1.25, HEX["N"]))
    svg = '<svg>\n' + "\n".join(paths) + '\n</svg>\n'
    hh, ww = rgba.shape[:2]
    svg = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ww} {hh}" width="{ww/S*4:.0f}" height="{hh/S*4:.0f}">\n<title>Combata - {name}</title>', svg, count=1)
    svg = re.sub(r'<\?xml[^>]*\?>\s*', '', svg)
    svg = re.sub(r'<!--.*?-->\s*', '', svg, flags=re.S)
    os.makedirs(f"{OUT}/SVG/{folder}", exist_ok=True)
    os.makedirs(f"{OUT}/PNG/{folder}", exist_ok=True)
    os.makedirs(f"{OUT}/JPG/{folder}", exist_ok=True)
    open(f"{OUT}/SVG/{folder}/{name}.svg", "w").write(svg)
    # renders
    longest = 4000
    if ww >= hh: ow, oh = longest, round(longest * hh / ww)
    else: oh, ow = longest, round(longest * ww / hh)
    png = f"{OUT}/PNG/{folder}/{name}.png"
    cairosvg.svg2png(bytestring=svg.encode(), write_to=png, output_width=ow, output_height=oh)
    im = Image.open(png).convert("RGBA")
    pd = int(max(im.size) * 0.06)
    bgc = Image.new("RGBA", (im.size[0] + 2*pd, im.size[1] + 2*pd), (255, 255, 255, 255))
    bgc.alpha_composite(im, (pd, pd))
    bgc.convert("RGB").save(f"{OUT}/JPG/{folder}/{name}.jpg", quality=95, subsampling=0, dpi=(300, 300))
    print(name, ow, oh, len(svg)//1024, "KB")

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for line in open(f"{W}/boxes.txt"):
        folder, name, *_ = line.split()
        if only and name not in only: continue
        process(name, folder)

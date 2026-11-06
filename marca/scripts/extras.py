import os, re, io, shutil
import cairosvg
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
O = D + "/out/Combata_Identidad_Visual_HQ"
N, L, P, V, C = "#1A0B3D", "#D9FF00", "#FF2EA6", "#B6A4FF", "#F5F4EE"

def render(svg, folder, name, longest=4000, jpg_bg=(255,255,255), square=None):
    for f in ("SVG", "PNG", "JPG"): os.makedirs(f"{O}/{f}/{folder}", exist_ok=True)
    open(f"{O}/SVG/{folder}/{name}.svg", "w").write(svg)
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    w, h = vb[2], vb[3]
    ow, oh = (longest, round(longest*h/w)) if w >= h else (round(longest*w/h), longest)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=ow, output_height=oh)
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    im.save(f"{O}/PNG/{folder}/{name}.png", dpi=(300, 300))
    pd = int(max(im.size) * 0.06) if folder != "07_Paleta" else 0
    bg = Image.new("RGBA", (im.size[0] + 2*pd, im.size[1] + 2*pd), jpg_bg + (255,)); bg.alpha_composite(im, (pd, pd))
    bg.convert("RGB").save(f"{O}/JPG/{folder}/{name}.jpg", quality=95, subsampling=0, dpi=(300, 300))
    return im

# 1) logo versions
src = open(f"{O}/SVG/01_Logotipos/logo_combata_principal.svg").read()
render(src.replace(N, "#FFFFFF").replace("logo_combata_principal", "logo_combata_blanco"), "01_Logotipos", "logo_combata_blanco", jpg_bg=(0x1A,0x0B,0x3D))
render(src.replace(N, L).replace("logo_combata_principal", "logo_combata_lima"), "01_Logotipos", "logo_combata_lima", jpg_bg=(0x1A,0x0B,0x3D))

# 2) favicon sizes + ico
for name in ("favicon_gafas", "favicon_sin_gafas"):
    svg = open(f"{O}/SVG/06_Favicon/{name}.svg").read()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    side = max(vb[2], vb[3])
    sq = re.sub(r'viewBox="[^"]+"', f'viewBox="{vb[0]-(side-vb[2])/2:.1f} {vb[1]-(side-vb[3])/2:.1f} {side:.1f} {side:.1f}"', svg)
    outd = f"{O}/PNG/06_Favicon/tamanos_web/{name}"; os.makedirs(outd, exist_ok=True)
    ims = []
    for s in (16, 32, 48, 64, 180, 192, 512):
        im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=sq.encode(), output_width=s, output_height=s))).convert("RGBA")
        n = {180: "apple-touch-icon-180", 192: "android-chrome-192", 512: "android-chrome-512"}.get(s, f"favicon-{s}")
        im.save(f"{outd}/{n}.png"); ims.append(im)
    big = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=sq.encode(), output_width=256, output_height=256))).convert("RGBA")
    big.save(f"{outd}/favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])

# 3) social profile pictures 1080 / 2048 full-bleed square
for name, bgc in (("avatar_nube_gafas", (0x1A,0x0B,0x3D)), ("avatar_nube_sin_gafas", (0xD9,0xFF,0x00))):
    im = Image.open(f"{O}/PNG/03_Avatares/{name}.png").convert("RGBA")
    side = int(max(im.size) * 1.22)
    for s in (1080, 2048):
        can = Image.new("RGBA", (side, side), bgc + (255,))
        can.alpha_composite(im, ((side-im.size[0])//2, (side-im.size[1])//2))
        os.makedirs(f"{O}/JPG/03_Avatares/perfil_redes", exist_ok=True)
        can.convert("RGB").resize((s, s), Image.LANCZOS).save(f"{O}/JPG/03_Avatares/perfil_redes/{name}_perfil_{s}.jpg", quality=95, subsampling=0)

# 4) palette
def cmyk(h):
    r, g, b = [int(h[i:i+2], 16)/255 for i in (1, 3, 5)]
    k = 1 - max(r, g, b)
    if k == 1: return (0, 0, 0, 100)
    return tuple(round(x*100) for x in ((1-r-k)/(1-k), (1-g-k)/(1-k), (1-b-k)/(1-k), k))
cols = [("Morado noche", N), ("Lima", L), ("Rosa", P), ("Lavanda", V), ("Crema", C)]
parts = []
for i, (nm, hx) in enumerate(cols):
    x = 60 + i*370
    rgb = tuple(int(hx[j:j+2], 16) for j in (1, 3, 5))
    parts.append(f'<rect x="{x}" y="60" width="330" height="330" rx="40" fill="{hx}" stroke="#E2DDF0" stroke-width="3"/>')
    parts.append(f'<text x="{x}" y="450" font-family="Sora" font-weight="700" font-size="34" fill="{N}">{nm}</text>')
    parts.append(f'<text x="{x}" y="500" font-family="Sora" font-weight="600" font-size="28" fill="{N}">{hx}</text>')
    parts.append(f'<text x="{x}" y="545" font-family="Sora" font-size="24" fill="{N}">RGB {rgb[0]} {rgb[1]} {rgb[2]}</text>')
    parts.append(f'<text x="{x}" y="585" font-family="Sora" font-size="24" fill="{N}">CMYK {" ".join(map(str, cmyk(hx)))} (aprox.)</text>')
pal = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 640" width="1900" height="640"><title>Combata - Paleta</title><rect width="1900" height="640" fill="#FFFFFF"/>{"".join(parts)}</svg>'
render(pal, "07_Paleta", "paleta_combata", longest=3800)
open(f"{O}/07_Paleta_colores.txt" if False else f"{O}/SVG/07_Paleta/paleta_combata.txt", "w").write(
    "\n".join(f"{nm}: {hx}  RGB {tuple(int(hx[j:j+2],16) for j in (1,3,5))}  CMYK aprox. {cmyk(hx)}" for nm, hx in cols) + "\n")

# 5) typography specimen
typ = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 700" width="1600" height="700"><title>Combata - Tipografia Sora</title>
<rect width="1600" height="700" fill="#FFFFFF"/>
<text x="60" y="440" font-family="Sora" font-weight="700" font-size="420" fill="{N}">Aa</text>
<text x="760" y="180" font-family="Sora" font-weight="700" font-size="110" fill="{N}">Sora</text>
<text x="760" y="280" font-family="Sora" font-weight="700" font-size="60" fill="{N}">Bold</text>
<text x="760" y="360" font-family="Sora" font-weight="600" font-size="60" fill="{N}">SemiBold</text>
<text x="760" y="440" font-family="Sora" font-weight="400" font-size="60" fill="{N}">Regular</text>
<text x="60" y="580" font-family="Sora" font-weight="400" font-size="40" fill="{N}">ABCDEFGHIJKLMNÑOPQRSTUVWXYZ abcdefghijklmnñopqrstuvwxyz</text>
<text x="60" y="640" font-family="Sora" font-weight="600" font-size="40" fill="{N}">0123456789 ¡! ¿? @ € % &amp; — Ponle un Combata.</text>
</svg>'''
im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=typ.encode(), output_width=3200))).convert("RGB")
os.makedirs(f"{O}/JPG/08_Tipografia", exist_ok=True); os.makedirs(f"{O}/PNG/08_Tipografia", exist_ok=True)
im.save(f"{O}/JPG/08_Tipografia/tipografia_sora.jpg", quality=95); im.save(f"{O}/PNG/08_Tipografia/tipografia_sora.png")
fd = f"{O}/Fuente_Sora"; os.makedirs(fd, exist_ok=True)
shutil.copy(D + "/Sora.ttf", fd + "/Sora-Variable.ttf")
print("ok")

"""
Bleomycin A2 – Stereochemistry Explorer
Zero RDKit / cheminformatics dependencies.
Only requires:  pip install streamlit
Molecule drawn as hand-coded SVG atom/bond graph.
"""

import streamlit as st
import math

st.set_page_config(
    page_title="Bleomycin A₂ · Stereo Explorer",
    page_icon="🧬",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:       #06080f;
  --surf:     #0e1220;
  --border:   #1c2238;
  --accent:   #39ffc8;
  --accent2:  #ff4f6d;
  --accent3:  #ffd166;
  --text:     #dde3f0;
  --muted:    #5a6480;
  --r:        #ff4f6d;
  --s:        #39ffc8;
}

html, body, [class*="css"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.8rem 2.5rem; max-width: 1500px; }

/* ── Hero ── */
.hero-wrap {
  display: flex; align-items: baseline; gap: 1rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1.2rem; margin-bottom: 1.8rem;
}
.hero-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 4rem; letter-spacing: 0.04em;
  background: linear-gradient(100deg, var(--accent) 0%, #4fc3f7 60%, #9b59ff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  line-height: 1; margin: 0;
}
.hero-sub {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem; color: var(--muted);
  letter-spacing: 0.15em; text-transform: uppercase;
}

/* ── Cards ── */
.card {
  background: var(--surf); border: 1px solid var(--border);
  border-radius: 14px; padding: 1.4rem; margin-bottom: 1.1rem;
}
.card-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 0.9rem;
}

/* ── Stat pills ── */
.stat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 0.7rem; margin-bottom: 1rem; }
.stat-box {
  background: #080b14; border: 1px solid var(--border);
  border-radius: 10px; padding: 0.8rem; text-align: center;
}
.stat-box .n { font-family:'Bebas Neue',sans-serif; font-size: 2.4rem; line-height:1; }
.stat-box .l { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; }
.n-t { color: var(--accent3); }
.n-r { color: var(--r); }
.n-s { color: var(--s); }

/* ── Legend ── */
.legend { display:flex; gap:1.2rem; font-family:'IBM Plex Mono',monospace; font-size:0.72rem; }
.ldot { width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px; }

/* ── Table ── */
.ct { width:100%; border-collapse:collapse; font-family:'IBM Plex Mono',monospace; font-size:0.76rem; }
.ct th { text-align:left; padding:0.4rem 0.7rem; border-bottom:1px solid var(--border);
         color:var(--muted); font-size:0.6rem; text-transform:uppercase; letter-spacing:0.1em; }
.ct td { padding:0.38rem 0.7rem; border-bottom:1px solid #141828; }
.ct tr:last-child td { border-bottom:none; }
.badge { display:inline-block; border-radius:4px; padding:1px 7px; font-weight:600; font-size:0.7rem; }
.bR { background:rgba(255,79,109,.13); color:var(--r); border:1px solid rgba(255,79,109,.3); }
.bS { background:rgba(57,255,200,.1); color:var(--s); border:1px solid rgba(57,255,200,.3); }

/* ── Info box ── */
.infobox {
  background:rgba(57,255,200,.04); border-left:3px solid var(--accent);
  padding:0.8rem 1rem; border-radius:0 8px 8px 0;
  font-size:0.83rem; line-height:1.65; color:#9bacc0;
}

/* ── Distribution bar ── */
.dist-bar-wrap { height:8px; background:#080b14; border-radius:6px; overflow:hidden; margin-top:0.5rem; }
.dist-bar { height:100%; border-radius:6px; }

div[data-testid="stSelectbox"] label,
div[data-testid="stCheckbox"] label {
  font-family:'IBM Plex Mono',monospace !important;
  font-size:0.68rem !important;
  color:var(--muted) !important;
  text-transform:uppercase; letter-spacing:0.08em;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BLEOMYCIN A2 – HAND-CODED ATOM/BOND GRAPH
# Coordinates are in a 0-1000 x 0-600 canvas.
# Based on the published 2D depiction (Takita et al., JACS 1978).
# ─────────────────────────────────────────────────────────────────────────────

# atom: id, label, x, y, config (R/S/None), ring_member
ATOMS = [
    # ── Bithiazole ring 1 ──
    {"id":0,  "label":"C",  "x":68,  "y":310, "cfg":None},
    {"id":1,  "label":"N",  "x":95,  "y":270, "cfg":None},
    {"id":2,  "label":"C",  "x":138, "y":268, "cfg":None},   # C4 thiazole
    {"id":3,  "label":"S",  "x":152, "y":316, "cfg":None},
    {"id":4,  "label":"C",  "x":110, "y":335, "cfg":None},   # C5 thiazole

    # ── Bithiazole ring 2 ──
    {"id":5,  "label":"C",  "x":175, "y":250, "cfg":None},
    {"id":6,  "label":"N",  "x":215, "y":248, "cfg":None},
    {"id":7,  "label":"C",  "x":235, "y":210, "cfg":None},
    {"id":8,  "label":"S",  "x":205, "y":185, "cfg":None},
    {"id":9,  "label":"C",  "x":170, "y":210, "cfg":None},

    # ── Methylamine tail from thiazole 2 ──
    {"id":10, "label":"C",  "x":270, "y":250, "cfg":None},   # CONH
    {"id":11, "label":"N",  "x":308, "y":235, "cfg":None},
    {"id":12, "label":"C",  "x":345, "y":252, "cfg":None},
    {"id":13, "label":"C",  "x":382, "y":237, "cfg":None},
    {"id":14, "label":"N",  "x":418, "y":252, "cfg":None},   # terminal NH2

    # ── Peptide chain ──
    # Threonine-like  [C@@H](O) → S
    {"id":15, "label":"C",  "x":270, "y":300, "cfg":"S"},
    {"id":16, "label":"O",  "x":270, "y":340, "cfg":None},

    # Asn-like  [C@@H](CC(N)=O) → S
    {"id":17, "label":"C",  "x":308, "y":315, "cfg":"S"},
    {"id":18, "label":"C",  "x":328, "y":348, "cfg":None},
    {"id":19, "label":"N",  "x":365, "y":348, "cfg":None},

    # Ala-like [C@@H](C) → S
    {"id":20, "label":"C",  "x":345, "y":300, "cfg":"S"},
    {"id":21, "label":"C",  "x":360, "y":332, "cfg":None},   # methyl

    # Dehydroaminobutyric → no chiral (sp2 double bond)
    {"id":22, "label":"C",  "x":382, "y":285, "cfg":None},
    {"id":23, "label":"C",  "x":418, "y":280, "cfg":None},   # =CH

    # His-like [C@@H](Cc1cnHcn1) → S
    {"id":24, "label":"C",  "x":452, "y":295, "cfg":"S"},
    {"id":25, "label":"C",  "x":475, "y":328, "cfg":None},
    # Imidazole ring
    {"id":26, "label":"C",  "x":510, "y":320, "cfg":None},
    {"id":27, "label":"N",  "x":530, "y":290, "cfg":None},
    {"id":28, "label":"C",  "x":515, "y":265, "cfg":None},
    {"id":29, "label":"N",  "x":488, "y":270, "cfg":None},

    # NH2 terminal
    {"id":30, "label":"N",  "x":452, "y":260, "cfg":None},

    # ── C-terminal mannosyl arm ──
    # [C@@H](CO)[C@H](O)  → R then S
    {"id":31, "label":"C",  "x":240, "y":318, "cfg":"R"},
    {"id":32, "label":"C",  "x":210, "y":340, "cfg":None},   # CO
    {"id":33, "label":"O",  "x":190, "y":360, "cfg":None},

    # [C@H](O) → S  para-methoxyphenyl
    {"id":34, "label":"C",  "x":240, "y":360, "cfg":"S"},
    {"id":35, "label":"O",  "x":240, "y":395, "cfg":None},

    # para-methoxyphenyl ring
    {"id":36, "label":"C",  "x":265, "y":415, "cfg":None},
    {"id":37, "label":"C",  "x":265, "y":450, "cfg":None},
    {"id":38, "label":"C",  "x":295, "y":468, "cfg":None},
    {"id":39, "label":"C",  "x":325, "y":450, "cfg":None},
    {"id":40, "label":"C",  "x":325, "y":415, "cfg":None},
    {"id":41, "label":"C",  "x":295, "y":397, "cfg":None},
    {"id":42, "label":"O",  "x":295, "y":500, "cfg":None},   # OMe
    {"id":43, "label":"C",  "x":295, "y":520, "cfg":None},   # Me

    # ── Aminosugar (gulose) ──
    {"id":44, "label":"O",  "x":75,  "y":360, "cfg":None},   # ring O
    {"id":45, "label":"C",  "x":55,  "y":390, "cfg":"R"},
    {"id":46, "label":"C",  "x":80,  "y":415, "cfg":"S"},
    {"id":47, "label":"C",  "x":110, "y":400, "cfg":"R"},
    {"id":48, "label":"C",  "x":130, "y":370, "cfg":"S"},
    {"id":49, "label":"C",  "x":110, "y":345, "cfg":None},   # C1 of sugar (O link)
    {"id":50, "label":"N",  "x":55,  "y":430, "cfg":None},   # NH2
    {"id":51, "label":"O",  "x":80,  "y":450, "cfg":None},   # OH
    {"id":52, "label":"O",  "x":130, "y":430, "cfg":None},   # OH
    {"id":53, "label":"C",  "x":150, "y":365, "cfg":None},   # CH2OH
    {"id":54, "label":"O",  "x":170, "y":380, "cfg":None},

    # ── Methylvalerate (S-sulfonium) side chain ──
    {"id":55, "label":"S",  "x":452, "y":180, "cfg":None},   # S+
    {"id":56, "label":"C",  "x":480, "y":160, "cfg":None},
    {"id":57, "label":"C",  "x":510, "y":175, "cfg":None},
    {"id":58, "label":"C",  "x":540, "y":155, "cfg":"S"},
    {"id":59, "label":"N",  "x":570, "y":170, "cfg":None},
    {"id":60, "label":"C",  "x":575, "y":200, "cfg":None},   # CONH2

    # ── Pyrimidoblamic acid connection ──
    {"id":61, "label":"C",  "x":418, "y":200, "cfg":None},
    {"id":62, "label":"C",  "x":385, "y":195, "cfg":None},
    {"id":63, "label":"N",  "x":370, "y":165, "cfg":None},
    {"id":64, "label":"C",  "x":385, "y":140, "cfg":None},
    {"id":65, "label":"N",  "x":415, "y":140, "cfg":None},
    {"id":66, "label":"C",  "x":430, "y":165, "cfg":None},
    # Amino on pyrimidine
    {"id":67, "label":"N",  "x":395, "y":115, "cfg":None},
]

# bonds: (from_id, to_id, order)   order: 1=single, 2=double, 3=aromatic
BONDS = [
    # Thiazole ring 1
    (0,1,2),(1,2,1),(2,3,1),(3,4,1),(4,0,2),
    # Thiazole ring 2
    (5,6,2),(6,7,1),(7,8,1),(8,9,1),(9,5,2),
    # Bithiazole inter-ring bond
    (2,5,1),
    # Amide from thiazole2 C4 to peptide
    (7,10,1),(10,11,2),(10,15,1),
    # Methylamine tail
    (10,11,1),(11,12,1),(12,13,1),(13,14,1),
    # Peptide backbone bonds
    (15,17,1),(17,20,1),(20,22,1),(22,24,1),
    # Side chains
    (15,16,1),  # OH
    (17,18,1),(18,19,1),  # Asn side
    (20,21,1),  # Ala methyl
    (22,23,2),  # double bond dehydro
    (24,25,1),(25,26,1),  # His CH2 to imidazole
    # Imidazole ring
    (26,27,2),(27,28,1),(28,29,1),(29,26,1),(29,24,1),
    (24,30,1),  # terminal NH2
    # Amide carbonyls (N-C=O simplified)
    (15,31,1),(31,32,1),(32,33,1),
    (31,34,1),(34,35,1),
    # para-methoxyphenyl ring
    (35,36,1),(36,37,2),(37,38,1),(38,39,2),(39,40,1),(40,41,2),(41,36,1),
    (38,42,1),(42,43,1),
    # Sugar ring
    (44,45,1),(45,46,1),(46,47,1),(47,48,1),(48,49,1),(49,44,1),
    (45,50,1),(46,51,1),(47,52,1),(48,53,1),(53,54,1),
    # Sugar connects to main scaffold
    (4,44,1),
    # Sulfonium / methylvalerate
    (24,55,1),(55,56,1),(56,57,1),(57,58,1),(58,59,1),(59,60,1),
    # Pyrimidine
    (61,62,1),(62,63,2),(63,64,1),(64,65,2),(65,66,1),(66,61,2),
    (64,67,1),  # amino
    (61,24,1),(66,55,1),
]

# Chiral centres with CIP config
CHIRAL = {a["id"]: a["cfg"] for a in ATOMS if a["cfg"]}

# ─────────────────────────────────────────────────────────────────────────────
# SVG RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def build_svg(highlight="all", show_idx=False, width=980, height=580):
    atom_map = {a["id"]: a for a in ATOMS}

    R_COLOR   = "#ff4f6d"
    S_COLOR   = "#39ffc8"
    BOND_COL  = "#4a5568"
    ATOM_TEXT = "#dde3f0"
    HALO_R    = "#ff4f6d"
    HALO_S    = "#39ffc8"
    BG        = "#f9f9f6"

    lines = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:{BG};border-radius:12px;width:100%;">',
        # subtle grid
        '<defs><pattern id="g" width="30" height="30" patternUnits="userSpaceOnUse">'
        '<path d="M 30 0 L 0 0 0 30" fill="none" stroke="#e8e8e2" stroke-width="0.4"/>'
        '</pattern></defs>',
        f'<rect width="{width}" height="{height}" fill="url(#g)"/>',
    ]

    # ── Draw bonds ──
    for (a, b, order) in BONDS:
        if a not in atom_map or b not in atom_map:
            continue
        ax, ay = atom_map[a]["x"], atom_map[a]["y"]
        bx, by = atom_map[b]["x"], atom_map[b]["y"]

        if order == 2:
            # offset parallel line
            dx, dy = bx - ax, by - ay
            length  = math.hypot(dx, dy) or 1
            nx, ny  = -dy/length*3, dx/length*3
            lines.append(
                f'<line x1="{ax+nx:.1f}" y1="{ay+ny:.1f}" x2="{bx+nx:.1f}" y2="{by+ny:.1f}" '
                f'stroke="{BOND_COL}" stroke-width="1.8" stroke-linecap="round"/>'
            )
            lines.append(
                f'<line x1="{ax-nx:.1f}" y1="{ay-ny:.1f}" x2="{bx-nx:.1f}" y2="{by-ny:.1f}" '
                f'stroke="{BOND_COL}" stroke-width="1.8" stroke-linecap="round"/>'
            )
        else:
            lines.append(
                f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" '
                f'stroke="{BOND_COL}" stroke-width="2" stroke-linecap="round"/>'
            )

    # ── Draw atoms ──
    for atom in ATOMS:
        i = atom["id"]
        x, y = atom["x"], atom["y"]
        lbl  = atom["label"]
        cfg  = atom["cfg"]

        show_halo = (
            (highlight == "all"  and cfg in ("R","S")) or
            (highlight == "R"    and cfg == "R") or
            (highlight == "S"    and cfg == "S")
        )

        # Glow halo
        if show_halo:
            hcol = HALO_R if cfg == "R" else HALO_S
            lines.append(
                f'<circle cx="{x}" cy="{y}" r="14" fill="{hcol}" opacity="0.22"/>'
            )
            lines.append(
                f'<circle cx="{x}" cy="{y}" r="10" fill="{hcol}" opacity="0.35"/>'
            )

        # Atom background circle (white) so labels are readable
        if lbl != "C":
            lines.append(
                f'<circle cx="{x}" cy="{y}" r="11" fill="{BG}" stroke="none"/>'
            )

        # Label
        if lbl == "C" and not show_idx:
            # Carbon shown as dot only unless highlighted
            if show_halo:
                col = HALO_R if cfg == "R" else HALO_S
                lines.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{col}"/>')
        else:
            col = "#1a1a2e"
            if lbl == "N":   col = "#2563eb"
            elif lbl == "O": col = "#dc2626"
            elif lbl == "S": col = "#d97706"
            lines.append(
                f'<text x="{x}" y="{y+5}" text-anchor="middle" '
                f'font-family="IBM Plex Mono,monospace" font-size="11" '
                f'font-weight="600" fill="{col}">{lbl}</text>'
            )

        # R/S annotation badge
        if cfg and show_halo:
            badge_col = HALO_R if cfg == "R" else HALO_S
            lines.append(
                f'<rect x="{x+8}" y="{y-20}" width="16" height="13" rx="3" '
                f'fill="{badge_col}" opacity="0.9"/>'
            )
            lines.append(
                f'<text x="{x+16}" y="{y-10}" text-anchor="middle" '
                f'font-family="IBM Plex Mono,monospace" font-size="9" '
                f'font-weight="700" fill="#05070d">{cfg}</text>'
            )

        # Atom index
        if show_idx:
            lines.append(
                f'<text x="{x}" y="{y-15}" text-anchor="middle" '
                f'font-family="IBM Plex Mono,monospace" font-size="8" '
                f'fill="#888">{i}</text>'
            )

    # ── Fragment labels (region callouts) ──
    labels = [
        (72,  230, "Bithiazole"),
        (295, 540, "p-Methoxyphenyl"),
        (75,  475, "Aminosugar\n(Gulose)"),
        (520, 145, "Sulfonium"),
        (410, 110, "Pyrimidine"),
        (460, 320, "Imidazole"),
        (390, 240, "Peptide chain"),
    ]
    for lx, ly, txt in labels:
        for i, part in enumerate(txt.split("\n")):
            lines.append(
                f'<text x="{lx}" y="{ly + i*12}" text-anchor="middle" '
                f'font-family="IBM Plex Mono,monospace" font-size="8.5" '
                f'font-style="italic" fill="#9bacc0" opacity="0.8">{part}</text>'
            )

    lines.append("</svg>")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# CHIRAL DATA  (hard-coded from literature)
# ─────────────────────────────────────────────────────────────────────────────
CHIRAL_TABLE = [
    # (atom_id, element, CIP, fragment, notes)
    (15, "C", "S", "Peptide", "α-carbon, Thr-like"),
    (17, "C", "S", "Peptide", "α-carbon, Asn-like"),
    (20, "C", "S", "Peptide", "α-carbon, Ala-like"),
    (24, "C", "S", "Peptide", "α-carbon, His-like"),
    (31, "C", "R", "Mannosyl arm", "C-terminal hydroxyl carbon"),
    (34, "C", "S", "Mannosyl arm", "Benzylic chiral centre"),
    (45, "C", "R", "Aminosugar", "C2 of gulose"),
    (46, "C", "S", "Aminosugar", "C3 of gulose"),
    (47, "C", "R", "Aminosugar", "C4 of gulose"),
    (48, "C", "S", "Aminosugar", "C5 of gulose"),
    (58, "C", "S", "Sulfonium chain", "Methylvalerate α-C"),
]

R_IDS = {r[0] for r in CHIRAL_TABLE if r[2]=="R"}
S_IDS = {r[0] for r in CHIRAL_TABLE if r[2]=="S"}

# ─────────────────────────────────────────────────────────────────────────────
# MOLECULAR FACTS  (from literature, no computation needed)
# ─────────────────────────────────────────────────────────────────────────────
MOL_FACTS = {
    "Molecular formula":    "C₅₅H₈₄N₁₇O₂₁S₃⁺",
    "Exact MW":             "1415.55 Da",
    "H-bond donors":        "13",
    "H-bond acceptors":     "22",
    "Rotatable bonds":      "38",
    "Stereocentres":        "11",
    "TPSA":                 "~486 Ų",
    "LogP (est.)":          "−4.9",
}

# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <h1 class="hero-title">Bleomycin A₂</h1>
  <span class="hero-sub">Stereochemistry Explorer · 11 Chiral Centres · R/S Mapper</span>
</div>
""", unsafe_allow_html=True)

col_mol, col_panel = st.columns([3, 2], gap="large")

with col_panel:
    # Stats
    r_n, s_n, t_n = len(R_IDS), len(S_IDS), len(CHIRAL_TABLE)
    st.markdown(f"""
    <div class="card">
      <div class="card-label">Stereochemistry Summary</div>
      <div class="stat-grid">
        <div class="stat-box"><div class="n n-t">{t_n}</div><div class="l">Total centres</div></div>
        <div class="stat-box"><div class="n n-r">{r_n}</div><div class="l">R config</div></div>
        <div class="stat-box"><div class="n n-s">{s_n}</div><div class="l">S config</div></div>
      </div>
      <div class="legend">
        <span><span class="ldot" style="background:#ff4f6d"></span>R carbon</span>
        <span><span class="ldot" style="background:#39ffc8"></span>S carbon</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    st.markdown('<div class="card"><div class="card-label">Display Options</div>', unsafe_allow_html=True)
    hl = st.selectbox("Highlight mode", ["All chiral centres", "R centres only", "S centres only", "None"])
    show_idx = st.checkbox("Show atom indices", value=False)
    st.markdown('</div>', unsafe_allow_html=True)

    hl_key = {"All chiral centres":"all","R centres only":"R","S centres only":"S","None":"none"}[hl]

    # Chiral table
    rows = ""
    filter_cfg = None if hl_key=="all" else hl_key if hl_key in ("R","S") else None
    for aid, elem, cfg, frag, note in CHIRAL_TABLE:
        if hl_key not in ("all","none") and cfg != hl_key:
            continue
        badge = f'<span class="badge b{cfg}">{cfg}</span>'
        rows += f"<tr><td style='color:#5a6480'>{aid}</td><td>{elem}</td><td>{badge}</td><td style='color:#7a8aaa'>{frag}</td></tr>"

    shown = len([r for r in CHIRAL_TABLE if hl_key=="all" or hl_key=="none" or r[2]==hl_key])
    st.markdown(f"""
    <div class="card">
      <div class="card-label">Chiral Centres ({shown} shown)</div>
      <table class="ct">
        <thead><tr><th>Atom</th><th>Elem</th><th>Config</th><th>Fragment</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    # Mol properties
    prop_rows = "".join(
        f"<tr><td style='color:#5a6480'>{k}</td><td style='font-family:IBM Plex Mono,monospace'>{v}</td></tr>"
        for k,v in MOL_FACTS.items()
    )
    st.markdown(f"""
    <div class="card">
      <div class="card-label">Molecular Properties</div>
      <table class="ct"><tbody>{prop_rows}</tbody></table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="infobox">
      <strong style="color:#dde3f0">Bleomycin A₂</strong> is a glycopeptide antibiotic from
      <em>Streptomyces verticillus</em>, used clinically for Hodgkin's lymphoma and testicular cancer.
      <br><br>
      Its 11 stereocentres span a bithiazole chromophore, a linear peptide chain,
      an aminosugar (gulose), and a mannosyl-like arm — all essential for
      Fe²⁺ chelation and oxidative DNA cleavage.
      <br><br>
      R/S assignments based on Takita <em>et al.</em>, JACS 1978 and confirmed by
      Umezawa total synthesis.
    </div>
    """, unsafe_allow_html=True)

with col_mol:
    st.markdown('<div class="card"><div class="card-label">2D Structure — Bleomycin A₂</div>', unsafe_allow_html=True)
    svg = build_svg(highlight=hl_key, show_idx=show_idx)
    st.markdown(svg, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Fragment legend
    frags = [
        ("Bithiazole", "#4fc3f7",     "DNA intercalation chromophore"),
        ("Peptide chain", "#c084fc",  "11 stereocentres, metal coordination"),
        ("Aminosugar", "#fb923c",     "Cell-targeting, membrane interaction"),
        ("Sulfonium", "#facc15",      "Onium group, reactive warhead"),
        ("Pyrimidine", "#86efac",     "Metal binding nitrogen base"),
    ]
    cols = st.columns(len(frags))
    for col, (name, color, desc) in zip(cols, frags):
        with col:
            st.markdown(f"""
            <div style="border-top:3px solid {color};padding-top:0.5rem;margin-top:0.3rem">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:{color};letter-spacing:0.1em;text-transform:uppercase">{name}</div>
              <div style="font-size:0.72rem;color:#7a8aaa;margin-top:0.2rem;line-height:1.4">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DISTRIBUTION SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="card-label" style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;letter-spacing:0.18em;text-transform:uppercase;color:#39ffc8;margin-bottom:0.8rem">R/S Configuration Distribution</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, cfg, color, n in [
    (c1, "R", "#ff4f6d", r_n),
    (c2, "S", "#39ffc8", s_n),
    (c3, "Total", "#ffd166", t_n),
]:
    pct = int(n/t_n*100) if t_n else 0
    with col:
        st.markdown(f"""
        <div style="background:#0e1220;border:1px solid #1c2238;border-radius:12px;padding:1.1rem;text-align:center">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:2.8rem;color:{color};line-height:1">{n}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#5a6480;text-transform:uppercase;letter-spacing:0.1em">{cfg} Configuration</div>
          <div class="dist-bar-wrap" style="margin-top:0.7rem">
            <div class="dist-bar" style="background:{color};width:{pct}%"></div>
          </div>
          <div style="font-size:0.68rem;color:#5a6480;margin-top:0.3rem;font-family:'IBM Plex Mono',monospace">{pct}% of stereocentres</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEREOCENTRE DETAIL ACCORDION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📖 Detailed Stereocentre Notes"):
    for aid, elem, cfg, frag, note in CHIRAL_TABLE:
        badge_col = "#ff4f6d" if cfg=="R" else "#39ffc8"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;padding:0.5rem 0;border-bottom:1px solid #1c2238">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#5a6480;width:50px">#{aid}</span>
          <span style="background:{badge_col}22;color:{badge_col};border:1px solid {badge_col}55;
                       border-radius:4px;padding:1px 8px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;font-weight:700">{cfg}</span>
          <span style="font-size:0.82rem;color:#9bacc0"><strong style="color:#dde3f0">{frag}</strong> — {note}</span>
        </div>
        """, unsafe_allow_html=True)

with st.expander("🔬 About Bleomycin Mechanism"):
    st.markdown("""
    <div class="infobox" style="margin-top:0.3rem">
    Bleomycin exerts its antitumour effect through <strong style="color:#dde3f0">oxidative DNA strand scission</strong>:
    <br><br>
    <strong style="color:#39ffc8">1. Metal chelation</strong> — The pyrimidoblamic acid and histidine-like residues
    chelate Fe²⁺ (or Cu²⁺), forming a tight octahedral complex.
    <br><br>
    <strong style="color:#39ffc8">2. Oxygen activation</strong> — Fe²⁺–BLM binds O₂, generating a reactive
    "activated bleomycin" (Fe³⁺–OOH) species.
    <br><br>
    <strong style="color:#39ffc8">3. DNA cleavage</strong> — The bithiazole intercalates into DNA while the
    activated iron complex abstracts the C4' hydrogen of deoxyribose, producing single- and
    double-strand breaks preferentially at 5'-GC and 5'-GT sequences.
    <br><br>
    <strong style="color:#39ffc8">4. Stereochemistry</strong> — All 11 stereocentres are required for the
    correct 3D shape. Even single epimerisation abolishes activity.
    </div>
    """, unsafe_allow_html=True)

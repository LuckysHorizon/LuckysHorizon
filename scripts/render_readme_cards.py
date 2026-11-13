#!/usr/bin/env python3
"""Render every README card as an animated, self-contained SVG.

Inputs : data/contributions.json (daily Action), assets/portrait.jpg,
         assets/icons/*.svg (original tech logos), fonts/*.woff (optional)
Outputs: cards/*.svg
STATIC=1 renders the final frame with no animation (for screenshots).
"""
import base64, calendar, datetime as dt, html, json, os, random, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"; OUT.mkdir(exist_ok=True)
STATIC = os.environ.get("STATIC") == "1"

# ---------- palette & type ----------
PAPER, CARD, INK, MUTED, LINE = "#F6F1E7", "#FFFDF8", "#14110F", "#6B645A", "#DDD5C4"
BLUE, RED, YELLOW = "#0E75B6", "#D9432F", "#F2B705"
GREENS = ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"]   # GitHub heatmap
SERIF = "'Instrument Serif',Georgia,'Times New Roman',serif"
SANS = "Geist,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'Geist Mono','Fira Code',Menlo,Consolas,monospace"

# ---------- your content (edit here) ----------
NAME1, NAME2 = "Manikanta", "Boda"
KICKER = "FULL-STACK & BACKEND ENGINEER · HYDERABAD"
TAGLINE = "I build production-grade systems: payments, offline-first apps and agentic AI."
STATUS = "Software Trainee, Agentic AI @ Kustard Technologies"
BADGE = "Open to work"
TILES = [  # tag, value, decimals, suffix, caption, sub, bg, fg
    ("BUILD", 99.5, 1, "%", "ReelHaus transaction success rate in production", "React · Node · PostgreSQL · Redis", BLUE, "#FFFFFF"),
    ("AI", 94, 0, "%", "Vidyapath AI accuracy in production, offline-first PWA", "React · PostgreSQL · PWA · JWT", RED, "#FFFFFF"),
    ("SOLVE", 480, 0, "+", "LeetCode problems solved, 9 badges. CodeChef 446+", "Java · Python · DSA", YELLOW, INK),
]
REPOS = [  # name, description, stack, live?, accent, tag
    ("ReelHaus", "Event booking portal with live seat tracking, QR ticketing and payments. 99.5% txn success in production.", ["React", "Node.js", "PostgreSQL", "Redis", "Cashfree", "Razorpay"], True, BLUE, None),
    ("TravelMind-AI", "Multi-agent AI travel planner built on LangGraph and MCP. I did the complete UI refactor.", ["Python", "LangGraph", "MCP", "FastAPI", "PostgreSQL"], True, RED, "UI REFACTOR"),
    ("TravelBilling", "Billing platform: JWT auth, Redis caching, FastAPI PDF microservice, Docker CI/CD.", ["React", "Spring Boot", "Supabase", "Redis", "FastAPI", "Docker"], False, YELLOW, None),
    ("LocallyLearn", "AI-ready desktop IDE. Local-first, offline, Monaco editor.", ["Tauri", "React", "TypeScript", "Monaco"], False, INK, None),
]
STACK = [  # row label, [(chip text, icon file in assets/icons or None)]
    ("Languages", [("Java", "java"), ("Python", "python"), ("TypeScript", "typescript"), ("JavaScript", "javascript")]),
    ("AI", [("Agentic AI", None), ("LangChain", "langchain"), ("LangGraph", "langgraph"), ("MCP", "mcp"), ("Groq", None), ("Prompt Engineering", None)]),
    ("Frontend", [("React", "react"), ("Next.js", "nextjs"), ("Tailwind CSS", "tailwind"), ("Bootstrap", "bootstrap"), ("HTML5", "html5"), ("CSS3", "css3")]),
    ("Backend", [("Spring Boot", "springboot"), ("Spring MVC", "spring"), ("Node.js", "nodejs"), ("Express", "express"), ("FastAPI", "fastapi"), ("Flask", "flask"), ("JWT", "jwt")]),
    ("Data", [("MySQL", "mysql"), ("PostgreSQL", "postgresql"), ("Redis", "redis"), ("Supabase", "supabase"), ("MongoDB", "mongodb")]),
    ("Cloud & DevOps", [("AWS S3", "aws"), ("Google Cloud", "googlecloud"), ("Docker", "docker"), ("GitHub Actions", "githubactions"), ("Render", "render"), ("Cloudflare", "cloudflare"), ("Vercel", "vercel")]),
]
CERTS = [  # title, issuer, year, icon or monogram letter
    ("B.Tech Computer Science", "IARE · CGPA 8.76", "2027", "E"),
    ("AWS Academy Graduate, Cloud Foundations", "Amazon Web Services", "2026", "aws"),
    ("Cloud Computing", "NPTEL", "2025", "N"),
    ("Java: OOP, Data Structures and Algorithms", "Scaler", "2024", "S"),
]
PORTFOLIO_URL = "manikantaboda.online"
CONNECT = [  # title, handle, icon
    ("LinkedIn", "manikanta-boda", "linkedin"),
    ("LeetCode", "ManikantaBoda · 480+", "leetcode"),
    ("CodeChef", "manikantaboda · 446+", "codechef"),
    ("Email", "manikantaboda07@gmail.com", "gmail"),
]

# ---------- helpers ----------
def esc(s, q=False): return html.escape(str(s), quote=q)

FONTS = [("Instrument Serif", "serif-400.woff"), ("Geist Mono", "mono-400.woff"), ("Geist", "sans-400.woff")]
def font_css(used):
    """Embed only the (subset) fonts a card actually uses, keeping each SVG small."""
    css = ""
    for fam, f in FONTS:
        key = f"'{fam}'" if fam != "Geist" else "Geist,"
        p = ROOT / "fonts" / f
        if key in used and p.exists():
            css += f"@font-face{{font-family:'{fam}';src:url(data:font/woff;base64,{base64.b64encode(p.read_bytes()).decode()})}}"
    return css

BASE = """
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.25)}100%{opacity:1;transform:scale(1)}}
@keyframes swing{0%{opacity:0;transform:translateY(60px) rotate(-7deg)}60%{opacity:1;transform:translateY(-8px) rotate(1.5deg)}80%{transform:translateY(2px) rotate(-.5deg)}100%{opacity:1;transform:none}}
@keyframes ring{0%{opacity:.6;transform:scale(.2)}100%{opacity:0;transform:scale(1)}}
@keyframes nudge{0%,100%{transform:translate(0,0)}50%{transform:translate(4px,-4px)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.a{animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.8,.2,1);transform-box:fill-box}
.inf{animation-iteration-count:infinite;animation-timing-function:ease-in-out}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
STATIC_CSS = "*{animation:none!important}"

def A(name, delay, dur=.6, origin="center", inf=False):
    return (f'class="a{" inf" if inf else ""}" style="animation-name:{name};animation-duration:{dur}s;'
            f'animation-delay:{delay:.2f}s;transform-origin:{origin}"')

def svg(w, h, body, defs="", title=""):
    css = font_css(body) + BASE + (STATIC_CSS if STATIC else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(title, True)}"><style>{css}</style><defs>{defs}</defs>{body}</svg>')

def save(name, s): (OUT / name).write_text(s, encoding="utf-8")
def frame(w, h, rx=18, fill=CARD, stroke=LINE):
    return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

_ic = {}
def icon(name, x, y, size, fallback_fill=BLUE):
    """Original logo as an embedded data-URI <image>; diamond if no logo."""
    p = ROOT / "assets" / "icons" / f"{name}.svg" if name else None
    if p and p.exists():
        _ic.setdefault(name, base64.b64encode(p.read_bytes()).decode())
        return f'<image href="data:image/svg+xml;base64,{_ic[name]}" x="{x}" y="{y}" width="{size}" height="{size}"/>'
    c, r = size / 2, size * .32
    return (f'<path d="M{x + c} {y + c - r}L{x + c + r} {y + c}L{x + c} {y + c + r}L{x + c - r} {y + c}Z" fill="{fallback_fill}"/>')

def count(x, y, val, dec, suffix, delay, size, fill, family=SERIF, suf=None, anchor="start"):
    """Number that counts up from zero: 18 SMIL <set> frames (CSS can't change text)."""
    suf = suf or round(size * .5)
    def one(t, inner="", extra=""):
        return (f'<text {extra}x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" '
                f'text-anchor="{anchor}">{t}<tspan font-size="{suf}">{esc(suffix)}</tspan>{inner}</text>')
    if STATIC: return one(f"{val:.{dec}f}")
    out = []
    for i in range(18):
        b = delay + i * .035
        s = f'<set attributeName="display" to="inline" begin="{b:.3f}s"' + (' dur=".035s"/>' if i < 17 else "/>")
        out.append(one(f"{val * i / 17:.{dec}f}", s, 'display="none" '))
    return "".join(out)

def shine(w, h, d, clip_id):
    if STATIC: return ""
    return (f'<g clip-path="url(#{clip_id})"><g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{w + 240} 0;{w + 240} 0" keyTimes="0;.35;1" dur="6s" begin="{d + 1.6}s" repeatCount="indefinite"/>'
            f'<rect x="-140" y="-20" width="70" height="{h + 40}" fill="#fff" opacity=".2" transform="skewX(-18)"/></g></g>')

# ---------- data ----------
def load_days():
    p = ROOT / "data" / "contributions.json"
    if p.exists():
        return {d["date"]: d["count"] for d in json.loads(p.read_text())["days"]}
    print("! data/contributions.json missing, using synthetic preview data")
    rnd, today, days = random.Random(7), dt.date.today(), {}
    for i in range(400):
        d = today - dt.timedelta(days=i)
        days[d.isoformat()] = 0 if rnd.random() < .3 else int(rnd.expovariate(1 / 4))
    return days

def stats(days):
    today = dt.date.today()
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)   # weeks start Sunday
    grid = [start + dt.timedelta(days=i) for i in range((today - start).days + 1)]
    cnt = [days.get(d.isoformat(), 0) for d in grid]
    months = []
    for k in range(11, -1, -1):
        mm, yy = today.month - k, today.year
        while mm <= 0: mm += 12; yy -= 1
        months.append((calendar.month_abbr[mm].upper(), sum(c for d, c in days.items() if d[:7] == f"{yy}-{mm:02d}")))
    longest = run = 0
    for c in cnt:
        run = run + 1 if c else 0; longest = max(longest, run)
    cur, i = 0, len(cnt) - 1
    if cnt and not cnt[i]: i -= 1
    while i >= 0 and cnt[i]: cur += 1; i -= 1
    bi = max(range(len(cnt)), key=lambda i: cnt[i])
    return dict(grid=grid, cnt=cnt, months=months, best=max(range(12), key=lambda i: months[i][1]),
                total=sum(cnt), active=sum(1 for c in cnt if c), cur=cur, longest=longest,
                busy=cnt[bi], busy_date=grid[bi].strftime("%d %b %Y"))

# ---------- cards ----------
def hero():
    w, h = 1000, 360
    px, py, ps = 676, 40, 280                      # photo card
    cx, cy = px + ps / 2, py + ps / 2
    fill2 = INK if STATIC else "url(#shine)"
    jpg = base64.b64encode((ROOT / "assets" / "portrait.jpg").read_bytes()).decode()
    defs = (f'<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="348" y2="0">'
            f'<stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>'
            f'<stop offset=".5" stop-color="{BLUE}"/><stop offset=".58" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" values="-300 0;300 0;300 0" '
            f'keyTimes="0;.4;1" dur="6s" begin="1.8s" repeatCount="indefinite"/></linearGradient>'
            f'<filter id="sh" x="-25%" y="-25%" width="150%" height="160%"><feDropShadow dx="0" dy="16" stdDeviation="14" '
            f'flood-color="#14110F" flood-opacity=".25"/></filter>'
            f'<clipPath id="pc"><rect x="{px + 10}" y="{py + 10}" width="{ps - 20}" height="{ps - 20}" rx="26"/></clipPath>')
    photo = (f'<g {A("swing", .35, 1.1, "50% 100%")}>'
             f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" rx="36" fill="{BLUE}" transform="rotate(-6 {cx} {cy})"/>'
             f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" rx="36" fill="{YELLOW}" transform="rotate(3 {cx} {cy})"/>'
             f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" rx="36" fill="{CARD}" stroke="{LINE}" stroke-width="2" filter="url(#sh)"/>'
             f'<image href="data:image/jpeg;base64,{jpg}" x="{px + 10}" y="{py + 10}" width="{ps - 20}" height="{ps - 20}" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>'
             f'<rect x="{px + 10}" y="{py + 10}" width="{ps - 20}" height="{ps - 20}" rx="26" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1.5"/>'
             f'{shine(ps, ps, .35, "pc") if False else ""}</g>')
    badge = (f'<g {A("rise", 1.3, .6)}><rect x="{px - 22}" y="{py + ps - 38}" width="196" height="36" rx="18" fill="{INK}"/>'
             f'<circle {A("pulse", 1.6, 1.6, inf=True)} cx="{px - 4}" cy="{py + ps - 20}" r="5" fill="#40C463"/>'
             f'<text x="{px + 10}" y="{py + ps - 15}" font-family="{MONO}" font-size="12.5" fill="#fff">{esc(BADGE)}</text></g>')
    b = [frame(w, h),
         f'<g {A("fade", .1)}><text x="48" y="60" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{MUTED}">{esc(KICKER)}</text></g>',
         f'<g {A("rise", .25, .8)}><text x="48" y="150" font-family="{SERIF}" font-size="88" fill="{INK}">{esc(NAME1)}</text></g>',
         f'<g {A("rise", .45, .8)}><text x="48" y="238" font-family="{SERIF}" font-size="88" fill="{fill2}">{esc(NAME2)}</text></g>']
    for k, l in enumerate(textwrap.wrap(TAGLINE, 48)):
        b.append(f'<g {A("rise", .7 + k * .1)}><text x="48" y="{284 + k * 23}" font-family="{SANS}" font-size="17" fill="{MUTED}">{esc(l)}</text></g>')
    b.append(f'<g {A("fade", .9)}><circle {A("pulse", 1.2, 1.6, inf=True)} cx="54" cy="337" r="5" fill="{BLUE}"/>'
             f'<text x="70" y="342" font-family="{SANS}" font-size="14" fill="{INK}">{esc(STATUS)}</text></g>')
    b += [photo, badge]
    return svg(w, h, "".join(b), defs, f"{NAME1} {NAME2}, {KICKER}")

def graph(S):
    w, h, cell, gap = 1000, 226, 15, 3
    nz = sorted(c for c in S["cnt"] if c)
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]
    lvl = lambda c: 0 if c == 0 else 1 + (c > q[0]) + (c > q[1]) + (c > q[2])
    b = [frame(w, h),
         f'<text x="23" y="32" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">CONTRIBUTION GRAPH</text>',
         f'<text x="{w-23}" y="32" text-anchor="end" font-family="{MONO}" font-size="12" fill="{GREENS[3]}">{S["total"]:,} CONTRIBUTIONS IN THE LAST YEAR</text>']
    last_m = None
    for i, (d, c) in enumerate(zip(S["grid"], S["cnt"])):
        col, row = i // 7, i % 7
        x, y = 23 + col * (cell + gap), 62 + row * (cell + gap)
        if row == 0 and d.month != last_m:
            last_m = d.month
            b.append(f'<text x="{x}" y="52" font-family="{MONO}" font-size="10" fill="{MUTED}">{calendar.month_abbr[d.month].upper()}</text>')
        b.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{GREENS[lvl(c)]}" '
                 f'style="animation:pop .4s {.5 + col * .018:.2f}s both;transform-box:fill-box;transform-origin:center"/>')
    lx = w - 23 - 5 * 18 - 70
    b.append(f'<text x="{lx}" y="{h-16}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{MUTED}">LESS</text>')
    for k, g in enumerate(GREENS):
        b.append(f'<rect x="{lx + 8 + k * 18}" y="{h-27}" width="{cell}" height="{cell}" rx="3" fill="{g}"/>')
    b.append(f'<text x="{lx + 8 + 5 * 18 + 4}" y="{h-16}" font-family="{MONO}" font-size="10" fill="{MUTED}">MORE</text>')
    return svg(w, h, "".join(b), "", f"Contribution graph, {S['total']} contributions in the last year")

def activity(S):
    w, h = 1000, 340
    mx = max(c for _, c in S["months"]) or 1
    b = [frame(w, h),
         f'<text x="48" y="58" font-family="{SERIF}" font-size="32" fill="{INK}">Contributions per month</text>',
         f'<text x="48" y="80" font-family="{MONO}" font-size="12" fill="{MUTED}">{sum(c for _, c in S["months"]):,} IN THE LAST 12 MONTHS</text>']
    base, maxh = 270, 140
    for i, (lab, c) in enumerate(S["months"]):
        bh = max(3, c / mx * maxh); x = 48 + i * 48; best = i == S["best"]
        b.append(f'<rect {A("grow", .5 + i * .06, .7, "50% 100%")} x="{x}" y="{base - bh:.1f}" width="36" height="{bh:.1f}" rx="4" fill="{BLUE if best else "#2B2622"}"/>')
        b.append(f'<text x="{x + 18}" y="{base + 20}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{lab}</text>')
        if best:
            b.append(f'<g {A("pop", 1.4, .5)}><text x="{x + 18}" y="{base - bh - 10:.1f}" text-anchor="middle" font-family="{SERIF}" font-size="26" fill="{BLUE}">{c}</text></g>')
    blocks = [("CURRENT STREAK", S["cur"], " days", "Longest: %d days" % S["longest"]),
              ("ACTIVE DAYS", S["active"], " / 365", "days with a contribution"),
              ("BUSIEST DAY", S["busy"], " commits", S["busy_date"])]
    for i, (lab, v, suf, sub) in enumerate(blocks):       # 100px per block so nothing overlaps
        y0, d = 40 + i * 100, 1.0 + i * .3
        b.append(f'<g {A("fade", d)}><text x="700" y="{y0}" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{MUTED}">{lab}</text>'
                 f'<text x="700" y="{y0 + 78}" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(sub)}</text></g>')
        b.append(count(700, y0 + 56, v, 0, suf, d + .2, 48, INK if i else BLUE, suf=18))
    return svg(w, h, "".join(b), "", "Monthly contributions chart with streak stats")

def tile(i, t):
    tag, val, dec, suf, cap, sub, bg, fg = t
    w, h, d = 330, 300, .3 + i * .25
    defs = f'<clipPath id="c{i}"><rect width="{w}" height="{h}" rx="22"/></clipPath>'
    ring = f'<circle {A("ring", d + .8, 2.4, inf=True)} cx="{w - 44}" cy="44" r="32" fill="none" stroke="{fg}" stroke-width="2"/>'
    cap_lines = "".join(f'<text x="28" y="{212 + k * 22}" font-family="{SANS}" font-size="16" fill="{fg}">{esc(l)}</text>'
                        for k, l in enumerate(textwrap.wrap(cap, 28)))
    body = (f'<g {A("swing", d, 1.0, "50% 100%")}><rect width="{w}" height="{h}" rx="22" fill="{bg}"/>{shine(w, h, d, f"c{i}")}{ring}'
            f'<text x="28" y="48" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{fg}" opacity=".85">{tag}</text>'
            f'<g {A("nudge", d + 1.2, 1.8, inf=True)}><text x="{w - 52}" y="52" font-family="{SANS}" font-size="26" fill="{fg}">↗</text></g>'
            f'{count(28, 168, val, dec, suf, d + .6, 112, fg, suf=48)}{cap_lines}'
            f'<text x="28" y="{h - 26}" font-family="{MONO}" font-size="11" fill="{fg}" opacity=".8">{esc(sub)}</text></g>')
    return svg(w, h + 12, body, defs, f"{tag}: {val}{suf} {cap}")

def repo(i, r):
    name, desc, stack, live, accent, tag = r
    w, h = 490, 190
    b = [frame(w, h, 16), f'<rect x="1" y="26" width="6" height="{h-52}" rx="3" fill="{accent}"/>',
         f'<text x="30" y="58" font-family="{SERIF}" font-size="34" fill="{INK}">{esc(name)}</text>']
    if tag:
        tx = 30 + len(name) * 15 + 14; tw = len(tag) * 7.4 + 20
        b.append(f'<rect x="{tx}" y="38" width="{tw:.0f}" height="24" rx="12" fill="{accent}"/>'
                 f'<text x="{tx + tw / 2:.0f}" y="54" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="#fff">{tag}</text>')
    if live:
        b.append(f'<circle {A("pulse", 1.0, 1.6, inf=True)} cx="{w-80}" cy="30" r="4" fill="#30A14E"/>'
                 f'<text x="{w-70}" y="34" font-family="{MONO}" font-size="11" letter-spacing="2" fill="#30A14E">LIVE</text>')
    for k, l in enumerate(textwrap.wrap(desc, 58)[:3]):
        b.append(f'<text x="30" y="{92 + k * 20}" font-family="{SANS}" font-size="13.5" fill="{MUTED}">{esc(l)}</text>')
    x = 30
    for s in stack:
        pw = len(s) * 6.8 + 18
        if x + pw > w - 20: break
        b.append(f'<rect x="{x}" y="{h-44}" width="{pw:.0f}" height="24" rx="12" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
                 f'<text x="{x + pw / 2:.0f}" y="{h-28}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{INK}">{esc(s)}</text>')
        x += pw + 8
    return svg(w, h, f'<g {A("rise", .3 + i * .2, .7)}>{"".join(b)}</g>', "", f"{name}: {desc}")

def stack():
    w, x0, xmax = 1000, 200, 964
    b, y, n = [], 90, 0
    for lab, items in STACK:
        b.append(f'<text x="48" y="{y + 22}" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{MUTED}">{esc(lab.upper())}</text>')
        x = x0
        for name, ic in items:
            cw = (36 if ic else 26) + len(name) * 7.2 + 12
            if x + cw > xmax: x = x0; y += 42
            tx = x + (36 if ic else 26)
            b.append(f'<g {A("rise", .3 + n * .04, .5)}><rect x="{x}" y="{y}" width="{cw:.0f}" height="34" rx="17" fill="{PAPER}" stroke="{LINE}" stroke-width="1.5"/>'
                     f'{icon(ic, x + 10, y + 7, 20) if ic else icon(None, x + 8, y + 9, 16)}'
                     f'<text x="{tx}" y="{y + 22}" font-family="{MONO}" font-size="12" fill="{INK}">{esc(name)}</text></g>')
            x += cw + 8; n += 1
        y += 52
    h = y + 24
    head = [frame(w, h), f'<text x="48" y="58" font-family="{SERIF}" font-size="32" fill="{INK}">What I build with</text>']
    return svg(w, h, "".join(head + b), "", "Tech stack with logos")

def certs():
    w, rowh = 1000, 66
    h = 96 + len(CERTS) * rowh + 10
    b = [frame(w, h), f'<text x="48" y="58" font-family="{SERIF}" font-size="32" fill="{INK}">Education &amp; certifications</text>']
    for i, (title, issuer, year, ic) in enumerate(CERTS):
        y = 84 + i * rowh
        g = [f'<line x1="48" y1="{y}" x2="{w-48}" y2="{y}" stroke="{LINE}" stroke-width="1.5"/>',
             f'<rect x="48" y="{y + 12}" width="42" height="42" rx="12" fill="{PAPER}" stroke="{LINE}" stroke-width="1.5"/>']
        if len(ic) == 1:
            g.append(f'<text x="69" y="{y + 40}" text-anchor="middle" font-family="{SERIF}" font-size="24" fill="{BLUE}">{ic}</text>')
        else:
            g.append(icon(ic, 54, y + 18, 30))
        g += [f'<text x="108" y="{y + 31}" font-family="{SERIF}" font-size="24" fill="{INK}">{esc(title)}</text>',
              f'<text x="108" y="{y + 50}" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(issuer)}</text>',
              f'<rect x="{w-48-84}" y="{y + 20}" width="84" height="30" rx="15" fill="none" stroke="{BLUE}" stroke-width="1.5"/>',
              f'<text x="{w-48-42}" y="{y + 40}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{BLUE}">{year}</text>']
        b.append(f'<g {A("rise", .3 + i * .15, .6)}>{"".join(g)}</g>')
    return svg(w, h, "".join(b), "", "Education and certifications")

def portfolio():
    w, h, d = 1000, 230, .2
    defs = f'<clipPath id="pf"><rect width="{w}" height="{h}" rx="22"/></clipPath>'
    dots = "".join(f'<circle cx="{52 + k * 20}" cy="52" r="6" fill="{c}"/>' for k, c in enumerate([BLUE, RED, YELLOW]))
    body = (f'<g {A("swing", d, 1.0, "50% 100%")}><rect width="{w}" height="{h}" rx="22" fill="{INK}"/>{shine(w, h, d, "pf")}{dots}'
            f'<text x="48" y="92" font-family="{MONO}" font-size="13" letter-spacing="3" fill="#B9B1A3">MY PORTFOLIO</text>'
            f'<text x="48" y="156" font-family="{SERIF}" font-size="68" fill="#FFFDF8">{PORTFOLIO_URL}</text>'
            f'<text x="48" y="192" font-family="{SANS}" font-size="16" fill="#B9B1A3">Projects, case studies and how I work. Open to work and collaborations.</text>'
            f'<circle {A("ring", d + .8, 2.4, inf=True)} cx="{w-110}" cy="{h/2}" r="60" fill="none" stroke="{BLUE}" stroke-width="2"/>'
            f'<circle cx="{w-110}" cy="{h/2}" r="44" fill="{BLUE}"/>'
            f'<g {A("nudge", d + 1.2, 1.8, inf=True)}><text x="{w-110}" y="{h/2 + 14}" text-anchor="middle" font-family="{SANS}" font-size="40" fill="#fff">↗</text></g></g>')
    return svg(w, h + 12, body, defs, f"Portfolio: {PORTFOLIO_URL}")

def connect(i, c):
    title, handle, ic = c
    w, h = 250, 112
    body = (f'{frame(w, h, 16)}{icon(ic, 24, 22, 34)}'
            f'<text x="70" y="49" font-family="{SERIF}" font-size="28" fill="{INK}">{esc(title)}</text>'
            f'<g {A("nudge", 1.5 + i * .2, 1.8, inf=True)}><text x="{w-40}" y="46" font-family="{SANS}" font-size="20" fill="{MUTED}">↗</text></g>'
            f'<text x="24" y="92" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(handle)}</text>')
    return svg(w, h, f'<g {A("rise", .3 + i * .15, .6)}>{body}</g>', "", f"{title}: {handle}")

if __name__ == "__main__":
    S = stats(load_days())
    save("hero.svg", hero()); save("graph.svg", graph(S)); save("activity.svg", activity(S))
    for i, t in enumerate(TILES): save(f"tile-{i + 1}.svg", tile(i, t))
    for i, r in enumerate(REPOS): save(f"repo-{i + 1}.svg", repo(i, r))
    save("stack.svg", stack()); save("certs.svg", certs()); save("portfolio.svg", portfolio())
    for i, c in enumerate(CONNECT): save(f"connect-{i + 1}.svg", connect(i, c))
    print("rendered", len(list(OUT.glob("*.svg"))), "cards", "(STATIC)" if STATIC else "")

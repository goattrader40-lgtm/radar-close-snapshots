#!/usr/bin/env python3
"""Theme & Group Radar — nightly data build.

Usage: python3 -I pipeline.py <workdir> <out_dir> [owner/close-snapshot-repo]

Sources (all public GitHub, end-of-day):
  - rreichel3/US-Stock-Symbols  : nightly snapshot of every NASDAQ/NYSE/AMEX stock
                                  (last price, % change, volume, market cap, Nasdaq industry).
                                  Git history = one file per evening; since 2026-09-24 each
                                  evening's file holds the PREVIOUS session (see LAG_START).
  - optional owner/repo (3rd arg)  : the user's own GitHub Action snapshot taken ~4:10 PM ET,
                                  used for the newest session until the evening file catches up.
  - JerBouma/FinanceDatabase    : sector / industry classification per symbol.
  - datasets/s-and-p-500-companies : current S&P 500 members.
Writes <out_dir>/stocks.json, <out_dir>/themes.json, <out_dir>/build.json
"""
import csv, datetime, io, json, os, re, subprocess, sys, zoneinfo
from collections import Counter, defaultdict

WORK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
NY = zoneinfo.ZoneInfo("America/New_York")
MIN_MCAP = 300e6            # universe floor for group stats
G_PCT, G_MCAP, G_VOL = 4.0, 700e6, 700_000   # gainer rule (defaults; the portal's filter boxes can change them)
G_PRICE, G_ADR, G_DVOL = 5.0, 3.5, 30e6       # price >= $5, ADR% >= 3.5, 20-day avg $ volume >= $30M; plus close > 200-day SMA
ADR_N, SMA_N, M3 = 20, 200, 63                 # ADR% = 20-day average of (high / low - 1), Qullamaggie's formula
AVG_N = 30                  # sessions for average volume

# ---------------- theme map: (category, theme, ETFs, members) ----------------
T = [
 # Baskets tested for co-movement (daily moves with the market's move removed, 120 sessions to Oct 22, 2026);
 # extra names and the Alt Managers / BDC / Industrial Automation / Agribusiness groups came from etf.net theme ETF holdings
 # AI chips split (Oct 26, 2026, with the SMH move taken out): the big three and the CPU makers each trade as a pack;
 # the old basket only moved with SMH (+0.06 beyond semis)
 ("AI & Semis", "AI Compute (NVDA AVGO TSM)", "SMH SOXX", "NVDA AVGO TSM"),
 ("AI & Semis", "CPUs (AMD INTC ARM)", "SMH SOXX", "AMD INTC ARM"),
 ("AI & Semis", "Memory & Storage", "DRAM", "MU SNDK WDC STX"),
 # Semi equipment split (tested Oct 24-26, 2026, 120 and 60 sessions, with the shared semi move removed):
 # the big four front-end toolmakers and the subsystem suppliers each trade as their own pack
 # Oct 26, 2026 review (your OK): MARA GLXY -> Neoclouds only; ROST BURL TJX -> Off-price only; TXRH DRI -> Casual Dining only;
 # P -> AI Servers; dropped (under 0.5, no better fit): BA GE FDX UPS AFRM AXP XYZ COF BWXT ARGX ALNY FIVE CAVA LNG IBM
 ("AI & Semis", "Wafer Fab Equipment", "SMH SOXX", "ASML AMAT LRCX KLAC"),
 ("AI & Semis", "Semi Subsystems", "SOXX", "UCTT ICHR MKSI"),
 ("AI & Semis", "Semi Test & Packaging", "SOXX", "TER FORM COHU AEHR ONTO NVMI CAMT AMKR ENTG ACMR"),
 ("AI & Semis", "GaN & SiC Power", "XSD", "NVTS WOLF VSH GFS"),
 ("AI & Semis", "Analog & Auto Semis", "SOXX", "TXN ADI NXPI MCHP LSCC ON STM QCOM SYNA MPWR ALGM POWI RMBS"),
 ("AI & Semis", "AI Servers & ODMs", "RACK", "DELL SMCI HPE CLS JBL FLEX SANM NTAP P"),
 ("AI & Semis", "AI Networking", "RACK", "ANET CSCO CRDO ALAB NOK AVGO MRVL HPE CLS PENG"),
 ("AI & Semis", "Optics & CPO", "LYTE LUMA", "COHR LITE CIEN FN AAOI GLW MTSI AXTI POET SMTC VIAV TTMI TSEM MXL"),
 ("AI Infrastructure", "Data Center Power & Cooling", "GRID POWR", "VRT ETN GEV NVT HUBB MOD POWL TT CAT JCI CMI AMSC"),
 ("AI Infrastructure", "Data Center Builders & REITs", "DTCR PAVE", "EQIX DLR IRM FIX EME STRL MTZ PWR DY"),
 ("AI Infrastructure", "Power Generation (AI Power)", "XLU", "CEG VST NRG TLN"),
 ("AI Infrastructure", "Fuel Cells & On-site Power", "", "BE FCEL PLUG"),
 ("AI Infrastructure", "Nuclear & Uranium", "NLR URA URNM", "CCJ OKLO SMR LEU NNE UEC UUUU NXE DNN XE"),
 ("AI Infrastructure", "Neoclouds & AI Hosting", "NCLD WGMI", "CRWV NBIS IREN CIFR WULF APLD GLXY HUT BTDR CORZ KEEL CLSK RIOT MARA"),
 ("Software", "Enterprise SaaS", "IGV", "CRM NOW ADBE INTU WDAY ADSK TEAM HUBS SAP DOCU ASAN FRSH PEGA BOX GWRE RNG BSY"),
 ("Software", "IT Services & Consulting", "IGV", "IT CTSH EPAM GLOB EXLS DXC INFY G ACN"),
 ("Software", "Payroll & HR Software", "IGV", "ADP PAYX PAYC PCTY"),
 ("Software", "AI Software & Data", "AIQ IGV", "PLTR SNOW DDOG MDB ESTC AI PATH GTLB NOW PD NTNX DT"),
 ("Software", "Cybersecurity", "CIBR HACK BUG", "CRWD PANW FTNT ZS NET OKTA S RBRK TENB QLYS SAIL NTSK RPD"),
 ("Internet", "Internet Platforms", "FDN", "UBER DASH ABNB BKNG EXPE LYFT"),
 ("Internet", "China Internet", "KWEB", "BABA JD PDD TCOM BILI TME BEKE VIPS"),
 ("Internet", "Telecom", "IYZ", "T VZ TMUS"),
 ("Financials", "Crypto & Digital Assets", "IBIT BITQ", "COIN HOOD MSTR CRCL BMNR BLSH ASST BTGO XXI"),
 ("Financials", "Fintech & Payments", "FINX ARKF IPAY", "V MA PYPL FISV FIS TOST GPN"),
 ("Financials", "Brokers & Exchanges", "IAI", "SCHW CME ICE NDAQ CBOE LPLA RJF"),
 ("Financials", "Alt Asset Managers", "GPZ", "ARES KKR CG BX TPG APO BAM BN OWL"),
 ("Financials", "BDCs & Private Credit", "BIZD", "OBDC ARCC FSK GBDC OTF HTGC"),
 ("Financials", "Big Banks", "KBE XLF", "JPM BAC WFC C GS MS"),
 ("Financials", "LatAm Fintech & Banks", "EWZ", "XP BBD ITUB INTR PAGS STNE NU"),
 ("Financials", "Regional Banks", "KRE", "MTB FITB HBAN RF KEY CFG ZION WAL EWBC FHN USB PNC TFC FULT FNB ASB"),
 ("Industrial Frontier", "Aerospace & Defense", "ITA XAR", "LMT RTX NOC GD LHX HII TDG"),
 ("Industrial Frontier", "Defense Tech & Drones", "SHLD", "KTOS AVAV ONDS RCAT UMAC MRCY BBAI"),
 ("Industrial Frontier", "Space", "UFO ARKX", "SPCX RKLB ASTS PL LUNR FLY ECHO VSAT RDW IRDM BKSY VOYG MDA"),
 ("Industrial Frontier", "Industrial Automation", "AIRR", "AME TKR GTES ROK EMR TEX"),
 ("Industrial Frontier", "Quantum Computing", "QTUM", "IONQ RGTI QBTS QUBT ARQQ INFQ"),
 ("Clean Energy", "Solar & Clean Energy", "TAN ICLN", "FSLR ENPH NXT SEDG RUN ARRY CSIQ SHLS"),
 # Oil split (tested Oct 23, 2026): shale/Permian, majors, offshore drillers, LatAm, refiners each move as their own pack
 ("Energy", "Shale & Permian E&P", "XOP", "CHRD PR EOG DVN APA OXY COP OVV SM MTDR FANG CRGY NOG TALO MUR"),
 ("Energy", "Oil Majors", "XLE", "BP CVX SHEL EQNR XOM TTE PBR"),
 ("Energy", "Offshore Drillers", "OIH", "RIG VAL NE BORR"),
 ("Energy", "LatAm Energy", "ARGT", "VIST YPF PBR"),
 ("Energy", "Crude & Product Tankers", "BWET SEA", "FRO DHT INSW ECO NAT TRMD HAFN STNG"),
 ("Energy", "Refiners", "CRAK", "VLO PBF DINO PSX MPC DK PARR CVI"),
 ("Energy", "Natural Gas Producers", "FCG", "EQT EXE AR RRC CNX"),
 ("Energy", "Oil Services", "OIH", "SLB HAL BKR NOV FTI WFRD"),
 ("Metals & Mining", "Gold Miners", "GDX GDXJ", "NEM AEM B WPM FNV KGC AU GFI IAG AGI OR EQX BTG HMY ARIS"),
 ("Metals & Mining", "Silver Miners", "SIL", "PAAS AG HL CDE EXK SSRM"),
 ("Metals & Mining", "Copper & Base Metals", "COPX XME", "FCX SCCO AA BHP RIO HBM ERO TECK"),
 ("Metals & Mining", "Steel", "SLX", "NUE STLD CLF CMC"),
 ("Metals & Mining", "Rare Earths", "REMX", "MP USAR CRML TMC"),
 ("Materials", "Agribusiness & Fertilizer", "MOO", "ADM BG CF NTR DAR"),
 ("Healthcare", "Biotech", "XBI IBB", "VRTX REGN AMGN GILD BIIB INCY RPRX"),
 ("Healthcare", "Pharma & GLP-1", "XPH PPH", "LLY NVO MRK PFE ABBV JNJ BMY AZN NVS GSK SNY"),
 ("Healthcare", "Medtech", "IHI", "ISRG BSX SYK MDT ABT EW DXCM PODD STE ZBH BDX"),
 ("Healthcare", "Gene Editing", "ARKG", "CRSP BEAM NTLA"),
 ("Healthcare", "Genomics & Diagnostics", "ARKG", "TEM NTRA CAI TXG GH TWST GRAL ILMN"),
 ("Healthcare", "Life Science Tools & CROs", "XLV", "TMO DHR A WAT IQV CRL ICLR RGEN RVTY FTRE"),
 ("Healthcare", "Drug Distributors", "XLV", "COR MCK CAH"),
 ("Healthcare", "Managed Care", "IHF", "UNH ELV CI HUM CNC MOH CVS OSCR"),
 ("Consumer", "Homebuilders & Housing", "ITB XHB", "DHI LEN PHM NVR TOL KBH BLDR HD LOW MTH MAS OC"),
 ("Consumer", "Building Products", "XHB", "BLDR MAS FBIN OC TREX"),
 ("Consumer", "Off-price Retail", "XRT", "ROST TJX BURL"),
 ("Consumer", "Hotels", "PEJ", "HLT MAR H"),
 ("Consumer", "Cruise Lines", "PEJ", "CCL NCLH RCL"),
 ("Consumer", "Apparel & Mall Retail", "XRT", "ANF AEO GAP URBN"),
 ("Consumer", "Casual Dining", "PEJ", "DRI CAKE TXRH BLMN"),
 ("Consumer", "Retail", "XRT", "WMT COST TGT DG DLTR BJ"),
 ("Consumer", "Restaurants", "XLY", "MCD SBUX CMG YUM DPZ QSR"),
 ("Consumer", "Tobacco", "XLP", "PM MO BTI"),
 ("Consumer", "China EV", "KARS", "NIO XPEV LI"),
 ("Transports", "Airlines", "JETS", "DAL UAL AAL LUV ALK JBLU SKYW ULCC"),
 ("Transports", "Transports & Freight", "IYT", "UNP CSX NSC ODFL SAIA XPO JBHT CHRW SNDR KNX WERN"),
]
# Nasdaq-100 members (Wikipedia list as of Jun 2026; edit here when it changes)
NDX = set("""ADBE AMD ABNB ALNY GOOGL GOOG AMZN AEP AMGN ADI AAPL AMAT APP ARM ASML ALAB ADSK ADP AXON BKR BKNG AVGO
CDNS CTAS CSCO CCEP CMCSA CEG CPRT CRWV COST CRWD CSX DDOG DXCM FANG DASH EA EXC FAST FER FTNT GEHC GILD HON IDXX
INTC INTU ISRG KDP KLAC KHC LRCX LIN LITE MAR MRVL MELI META MCHP MU MSFT MSTR MDLZ MPWR MNST NBIS NFLX NVDA NXPI
ORLY ODFL PCAR PLTR PANW PAYX PYPL PDD PEP QCOM REGN RKLB ROP ROST SNDK STX SHOP SBUX SNPS TMUS TTWO TER TSLA TXN
TRI VRTX WMT WBD WDC WDAY XEL""".split())

def run(*a, cwd=None):
    subprocess.run(a, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fetch(url, dest):
    run("curl", "-sSfL", "-m", "120", "-o", dest, url)

# ---------------- 1. sources ----------------
uss = os.path.join(WORK, "uss")
if os.path.isdir(os.path.join(uss, ".git")):
    run("git", "fetch", "-q", "--shallow-since=330 days ago", "origin", "main", cwd=uss)
    run("git", "reset", "-q", "--hard", "origin/main", cwd=uss)
else:
    run("git", "clone", "-q", "--shallow-since=330 days ago", "--single-branch",
        "https://github.com/rreichel3/US-Stock-Symbols.git", uss)
fdb = os.path.join(WORK, "fdb")
if not os.path.isdir(os.path.join(fdb, ".git")):
    run("git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse",
        "https://github.com/JerBouma/FinanceDatabase.git", fdb)
    run("git", "sparse-checkout", "set", "database/equities", cwd=fdb)
else:
    run("git", "pull", "-q", cwd=fdb)
sp_csv = os.path.join(WORK, "sp500.csv")
fetch("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv", sp_csv)

def clone_or_update(url, dest, depth):
    try:
        if os.path.isdir(os.path.join(dest, ".git")):
            run("git", "fetch", "-q", "--depth", str(depth), "origin", cwd=dest)
            run("git", "reset", "-q", "--hard", "FETCH_HEAD", cwd=dest)
        else:
            run("git", "clone", "-q", "--depth", str(depth), url, dest)
        return True
    except subprocess.CalledProcessError:
        print(f"warning: could not read {url}", file=sys.stderr)
        return False

# ozkanpakdil/top-us-stock-tickers: each weekday ~4-6 AM ET saves Yahoo's close (OHLC) for the previous session.
ozk = os.path.join(WORK, "ozk")
HAVE_OZK = clone_or_update("https://github.com/ozkanpakdil/top-us-stock-tickers.git", ozk, 40)   # 40 days: daily highs/lows for ADR%
# Optional: the user's own repo; its GitHub Action saves Yahoo closes + volume at ~4:10 PM ET (close/latest.json).
CLOSE_REPO = sys.argv[3] if len(sys.argv) > 3 else ""
close_dir = os.path.join(WORK, "close")
if CLOSE_REPO and not clone_or_update(f"https://github.com/{CLOSE_REPO}.git", close_dir, 40):
    CLOSE_REPO = ""

# ---------------- 2. one snapshot per trading session ----------------
HOLIDAYS = {datetime.date.fromisoformat(d) for d in (   # NYSE full-day closures; extend each year
    "2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25 2026-06-19 2026-07-03 2026-09-07 2026-11-26 2026-12-25 "
    "2027-01-01 2027-01-18 2027-02-15 2027-03-26 2027-05-31 2027-06-18 2027-07-05 2027-09-06 2027-11-25 2027-12-24").split()}
def trading(d): return d.weekday() < 5 and d not in HOLIDAYS
def prev_trading(d):
    d -= datetime.timedelta(days=1)
    while not trading(d): d -= datetime.timedelta(days=1)
    return d

# rreichel3 saves its file around 8:40 PM ET. Since 2026-09-24 each file holds the PREVIOUS session's close
# (that night's file was an exact copy of the night before). Checked against published closes:
# NVDA $217.09 = Mon Oct 19 close, saved the evening of Tue Oct 20; SPCX $160.95 IPO close (Jun 12) saved Jun 12.
LAG_START = datetime.date(2026, 9, 24)

def commits(repo):
    w = subprocess.run(["git", "log", "--format=%H %cI"], cwd=repo, capture_output=True, text=True, check=True).stdout.split()
    return [(w[i], datetime.datetime.fromisoformat(w[i + 1]).astimezone(NY)) for i in range(0, len(w), 2)]

snap = {}   # session date -> (repo dir, commit, kind)
for sha, t in commits(uss):                                   # newest first
    d = t.date() if t.hour >= 16 else prev_trading(t.date())
    sess = prev_trading(d) if d >= LAG_START else (d if trading(d) else prev_trading(d))
    snap.setdefault(sess, (uss, sha, "evening file, next day"))
sessions = sorted(snap)[-215:]     # ~10 months: the 200-day SMA needs 200, 3M needs 63, the co-movement test 120

def num(s):
    s = (s or "").replace("$", "").replace(",", "").replace("%", "").strip()
    try: return float(s)
    except ValueError: return None

hist = defaultdict(dict)  # sym -> sess -> (price, pct, vol)
latest = {}
prev_sig, prev_px = None, {}
kept, breaks = [], []
CHECK = ("AAPL", "MSFT", "NVDA", "AMZN", "META", "TSLA", "GOOGL", "AVGO", "COST", "NFLX", "JPM", "XOM")
for sess in sessions:
    repo, sha, kind = snap[sess]
    rows = []
    for ex in ("nasdaq", "nyse", "amex"):
        txt = subprocess.run(["git", "show", f"{sha}:{ex}/{ex}_full_tickers.json"], cwd=repo,
                             capture_output=True, text=True, check=True).stdout
        for r in json.loads(txt):
            r["_ex"] = ex; rows.append(r)
    sig = tuple(sorted((r["symbol"], r["lastsale"]) for r in rows[:400]))
    if sig == prev_sig: continue          # same data saved twice -> keep one
    px = {r["symbol"]: (num(r["lastsale"]), num(r["pctchange"])) for r in rows if r["symbol"] in CHECK}
    if prev_px:   # does today's % change lead back to the previous file's price? (catches skipped or shifted days)
        good = [abs(p / (1 + c / 100) - prev_px[s][0]) / prev_px[s][0] < 0.003
                for s, (p, c) in px.items() if s in prev_px and p and c is not None and prev_px[s][0]]
        if good and sum(good) / len(good) < 0.8: breaks.append(str(sess))
    prev_sig, prev_px = sig, px
    kept.append(sess)
    for r in rows:
        hist[r["symbol"]][sess] = (num(r["lastsale"]), num(r["pctchange"]), num(r["volume"]))
        latest[r["symbol"]] = r
sessions = kept
kind_of = {d: snap[d][2] for d in sessions}

# ---- newer sessions the evening file doesn't have yet (Yahoo closes) ----
def git_show(repo, sha, path):
    r = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=repo, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

extra = {}   # session -> (kind, {symbol: (close, prev_close or None, volume or None)})
hl = defaultdict(dict)    # symbol -> session -> (high, low), Yahoo daily bars (US-domiciled stocks)
snapf = {}                # symbol -> row of the user's close snapshot for the newest session (Yahoo, all listings)
if HAVE_OZK:
    for sha, t in commits(ozk):
        if t.hour >= 16: sess = t.date() if trading(t.date()) else prev_trading(t.date())
        elif (t.hour, t.minute) < (9, 30): sess = prev_trading(t.date())
        else: continue                                           # saved during market hours: partial day
        if sess in extra: continue
        txt = git_show(ozk, sha, "tickers/all.csv")
        if not txt: continue
        d = {}
        for r in csv.DictReader(io.StringIO(txt)):
            c, hi, lo = num(r.get("close")), num(r.get("high")), num(r.get("low"))
            if not c: continue
            d[r["symbol"]] = (c, None, None)
            if hi and lo and hi >= lo > 0 and lo * 0.999 <= c <= hi * 1.001: hl[r["symbol"]][sess] = (hi, lo)
        extra[sess] = ("Yahoo close, saved next morning (no volume yet)", d)
if CLOSE_REPO:
    for sha, t in commits(close_dir):
        txt = git_show(close_dir, sha, "close/latest.json")
        if not txt: continue
        rows = json.loads(txt).get("rows", [])
        dates = Counter(r.get("date") for r in rows)
        if not dates: continue
        sess = datetime.date.fromisoformat(dates.most_common(1)[0][0])
        # use it only if it was saved after that day's 4 PM close (a run during market hours is a partial day)
        if not trading(sess) or t < datetime.datetime.combine(sess, datetime.time(16, 0), NY): continue
        if sess in extra and extra[sess][0].startswith("your close"): continue
        mine = [r for r in rows if r.get("date") == str(sess) and r.get("close")]
        extra[sess] = ("your close snapshot (Yahoo)",
                       {r["symbol"]: (num(str(r.get("close"))), num(str(r.get("prev_close"))), r.get("volume")) for r in mine})
        for r in mine:
            if r.get("high") and r.get("low"): hl[r["symbol"]].setdefault(sess, (float(r["high"]), float(r["low"])))
        if not snapf or sess > snapf["_sess"]:
            snapf = {r["symbol"]: r for r in mine}; snapf["_sess"] = sess
for sess in sorted(x for x in extra if x > sessions[-1]):
    kind, d = extra[sess]
    last = sessions[-1]
    if prev_trading(sess) != last:                                # a session in between is missing: stop here
        print(f"warning: no data for the session before {sess}; not adding it", file=sys.stderr); break
    upd, fill, moved = {}, {}, 0
    before = sessions[-2] if len(sessions) > 1 else None
    for s in latest:
        if s not in d: continue
        close, prev, vol = d[s]
        if last not in hist[s] and prev and before in hist[s] and hist[s][before][0]:
            # this listing is missing the previous day; this file's previous close fills it
            fill[s] = (prev, (prev / hist[s][before][0] - 1) * 100, None)
        p0 = fill[s][0] if s in fill else hist[s].get(last, (None,))[0]
        if not p0: continue
        upd[s] = (close, (close / (prev or p0) - 1) * 100, vol)
        moved += abs(close - p0) > 1e-9
    if not upd or moved / len(upd) < 0.5:                          # mostly unchanged prices: stale file
        print(f"warning: {kind} for {sess} looks stale; skipped", file=sys.stderr); break
    for s, v in fill.items(): hist[s][last] = v
    for s, (close, pct, vol) in upd.items():
        hist[s][sess] = (close, pct, vol)
        row = dict(latest[s]); old = num(row.get("lastsale")); row["lastsale"] = f"${close}"
        mc = num(row.get("marketCap"))
        if mc and old: row["marketCap"] = str(mc * close / old)
        latest[s] = row
    sessions.append(sess); kind_of[sess] = kind

asof = sessions[-1]
if breaks: print("warning: day-to-day prices don't chain at " + ", ".join(breaks), file=sys.stderr)

# ---------------- 3. classification + index membership ----------------
fd = {}
for f in ("NMS", "NYQ", "ASE", "NGM", "NCM", "PCX", "BTS"):
    p = os.path.join(fdb, "database", "equities", f + ".csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if r["industry"]: fd.setdefault(r["symbol"].replace("-", "/"), r)
sp500 = {r["Symbol"].replace(".", "/") for r in csv.DictReader(open(sp_csv, encoding="utf-8"))}

BAD = re.compile(r"warrant|\bright|\bunits?\b|preferred|\bnotes?\b|debenture|"
                 r"\bfund\b|\betf\b|\betn\b|trust units|municipal|%|subordinated|perpetual|strats", re.I)
FUNDLIKE = re.compile(r"clos(ed|e)[- ]?end(ed)?|unit investment trust|interval fund|management investment company", re.I)
def is_common(sym, name):
    if "^" in sym: return False
    if "/" in sym and not re.fullmatch(r"[A-Z]+/[A-C]", sym): return False
    if sym in fd and FUNDLIKE.search((fd[sym].get("summary") or "").split(". ")[0]): return False  # closed-end funds etc.
    return not BAD.search(re.sub(r"\([^)]*\)", "", name or ""))   # "(Each repstg 500 Preferred shares)" is an ADR note, not a preferred stock

def clean_name(n):
    n = re.sub(r"\s+(Class [A-C] )?(Common Stock|Ordinary Shares?|Common Shares|American Depositary Shares?|"
               r"Sponsored ADR|ADS|Registered Shares|Subordinate Voting Shares).*$", "", n or "", flags=re.I)
    return n.strip().rstrip(",")

# learn Nasdaq-industry -> FinanceDatabase-industry for names FD doesn't cover
votes = defaultdict(Counter)
for s, r in latest.items():
    if s in fd: votes[r["industry"]][(fd[s]["sector"], fd[s]["industry"])] += 1

# ---------------- 4. co-movement: auto-added members + auto groups (recomputed weekly) ----------------
# Same test used to approve the core baskets: daily % moves with the whole market's move removed (beta-adjusted),
# outliers clipped, over the 120 sessions ending at the most recent Friday. A stock joins when it tracks a group
# at >= 0.6, that group is its best fit, it shares a sector with the group, and it passes the liquidity floors.
COH_WINDOW, COH_FLOOR = 120, 0.6
AUTO_ANCHORS = [   # names for the groups the test finds; a group takes the first label with 2+ of these tickers
    ("Refiners", "VLO MPC PSX PBF DINO"), ("Pipelines & Midstream", "KMI WMB OKE ENB EPD TRP ET MPLX"),
    ("P&C Insurance & Brokers", "CB TRV PGR ALL AON AJG BRO WRB HIG"), ("Life Insurers", "MET PRU LNC EQH CRBG"),
    ("Paints & Coatings", "SHW PPG RPM AXTA"), ("Commodity Chemicals", "DOW LYB OLN WLK HUN CE"),
    ("Electric Utilities", "SO DUK AEP XEL ED NEE"), ("Multi-Utilities", "PEG EXC SRE"),
    ("Packaged Food", "GIS CAG CPB KHC SJM HSY MDLZ"), ("Beverages", "KO PEP STZ TAP DEO"),
    ("Household Products", "PG CL KMB CHD CLX"), ("Online Listings & Marketplaces", "Z ZG YELP CARG NRDS EVER"),
    ("Info Services & Staffing", "VRSK TRI EFX TRU RHI MAN UPWK"), ("Waste Management", "WM RSG WCN"),
    ("International Banks", "HSBC UBS DB BCS ING SAN MUFG SMFG RY TD BNS"), ("Life Science Tools", "TMO DHR A WAT IQV"),
    ("Small-cap Oilfield Services", "LBRT PUMP AESI WTTR KGS"), ("Tankers & Dry Bulk", "STNG INSW NAT SBLK HAFN"),
    ("Packaging", "AMCR CCK BALL IP AVY SON"), ("Retail REITs", "KIM REG SPG O NNN BRX"),
    ("Net Lease & Diversified REITs", "WPC VICI GLPI FRT"), ("Towers & Self-Storage REITs", "AMT CCI SBAC EXR PSA"),
    ("Mortgage REITs", "NLY AGNC STWD BXMT"), ("Health Care REITs", "WELL VTR OHI DOC"),
    ("Hotel REITs", "HST PK PEB DRH XHR SHO"), ("Industrial REITs", "PLD REXR STAG FR TRNO"),
    ("Residential REITs", "MAA CPT UDR INVH AMH"), ("Office REITs", "BXP SLG HIW CUZ"),
    ("Flow Control & Machinery", "GGG ITW XYL IR OTIS PNR MWA"),
]
AUTO_FALLBACK = {"Biotechnology": "Small & Mid-cap Biotech"}   # otherwise the industry name
core = {th: mem.split() for _, th, _, mem in T}
ext, auto, scores, strength = {}, [], {}, {}   # ext: theme -> [(score, sym)]; auto: [(name, [(score, sym)])]
coh_anchor = None
try:
    import numpy as np
    fri = asof - datetime.timedelta(days=(asof.weekday() - 4) % 7)
    win = [d for d in sessions if d <= fri][-COH_WINDOW:]
    coh_anchor = win[-1] if win else None
    if len(win) < 60: raise RuntimeError(f"only {len(win)} sessions of history")
    univ = [s for s, r in latest.items() if is_common(s, r["name"]) and (num(r["marketCap"]) or 0) >= 5e8]
    R = np.array([[hist[s][d][1] if d in hist[s] and hist[s][d][1] is not None else np.nan for s in univ] for d in win])
    keep = np.isfinite(R).mean(0) >= 0.9
    univ = [s for s, k in zip(univ, keep) if k]
    R = np.clip(R[:, keep], -25, 25)
    mkt = np.nanmean(R, axis=1); mc = mkt - mkt.mean()
    cols = []
    for j in range(R.shape[1]):
        y = R[:, j]; f = np.isfinite(y)
        b = np.dot(y[f] - y[f].mean(), mc[f]) / max(1e-9, (mc[f] ** 2).sum())
        e = y - b * mkt; sd = np.nanstd(e) or 1.0; e = np.clip(e, -3 * sd, 3 * sd)
        cols.append(np.nan_to_num((e - np.nanmean(e)) / (np.nanstd(e) or 1.0)))
    Z = np.array(cols).T
    col = {s: j for j, s in enumerate(univ)}
    def corr(a, b):
        a = a - a.mean(); b = b - b.mean(); dd = np.sqrt((a * a).sum() * (b * b).sum())
        return float((a * b).sum() / dd) if dd else 0.0
    groups = {th: [x for x in m if x in col] for th, m in core.items()}
    groups = {th: m for th, m in groups.items() if len(m) >= 3}
    gsum = {th: Z[:, [col[x] for x in m]].sum(1) for th, m in groups.items()}
    def gcorr(x, th):
        m = groups[th]; v = Z[:, col[x]]
        return corr(v, (gsum[th] - v) / (len(m) - 1)) if x in m else corr(v, gsum[th] / len(m))
    def best_fit(x):
        sc = {th: gcorr(x, th) for th in groups}; th = max(sc, key=sc.get); return th, sc[th]
    sector = lambda x: (fd.get(x) or {}).get("sector", "")
    for th, m in groups.items():
        for x in m: scores[(th, x)] = round(gcorr(x, th), 2)
    def avgvol(x):
        v = [hist[x][d][2] for d in win[-30:] if d in hist[x] and hist[x][d][2] is not None]
        return sum(v) / len(v) if v else 0
    incore = {x for m in core.values() for x in m}
    liquid = [x for x in univ if (num(latest[x]["marketCap"]) or 0) >= G_MCAP and avgvol(x) >= G_VOL]
    # AI & semis: everything there moves with SMH, so an auto-added name must also track its group with the
    # semi trade's move taken out (the average of all AI & semis basket names), at SEMI_FLOOR or better
    cat_of = {th: c for c, th, _, _ in T}
    semi_names = sorted({x for th, m in groups.items() if cat_of.get(th) == "AI & Semis" for x in m})
    semi_f = Z[:, [col[x] for x in semi_names]].mean(1) if semi_names else None
    def beyond(v):
        return v - (np.dot(v, semi_f) / np.dot(semi_f, semi_f)) * semi_f
    def beyond_fit(x, th):
        m = [y for y in groups[th] if y != x]
        return corr(beyond(Z[:, col[x]]), beyond(Z[:, [col[y] for y in m]].mean(1)))
    SEMI_FLOOR = 0.15
    for x in liquid:
        if x in incore: continue
        th, sc = best_fit(x)
        if sc >= COH_FLOOR and sector(x) in {sector(y) for y in groups[th]}:
            if cat_of.get(th) == "AI & Semis" and semi_f is not None and beyond_fit(x, th) < SEMI_FLOOR:
                continue
            ext.setdefault(th, []).append((round(sc, 2), x))
    taken = incore | {x for v in ext.values() for _, x in v}
    def prune(names, min_n=5):
        names = list(names)
        while len(names) >= min_n:
            Zm = Z[:, [col[x] for x in names]]; tot = Zm.sum(1)
            loo = {x: corr(Zm[:, i], (tot - Zm[:, i]) / (len(names) - 1)) for i, x in enumerate(names)}
            w = min(loo, key=loo.get)
            if loo[w] >= COH_FLOOR: return sorted(((round(v, 2), x) for x, v in loo.items()), reverse=True)
            names.remove(w)
        return []
    by_ind = defaultdict(list)
    for x in liquid:
        if x not in taken: by_ind[(fd.get(x) or {}).get("industry") or latest[x].get("industry") or "Other"].append(x)
    used_names = set(core)
    for ind, names in sorted(by_ind.items(), key=lambda kv: -len(kv[1])):
        rest = names
        for _ in range(3):
            g = prune(rest)
            if not g: break
            mem = {x for _, x in g}
            label = next((lab for lab, anc in AUTO_ANCHORS if len(mem & set(anc.split())) >= 2), AUTO_FALLBACK.get(ind, ind))
            base, k = label, 2
            while label in used_names: label, k = f"{base} {k}", k + 1
            used_names.add(label); auto.append((label, g))
            rest = [x for x in rest if x not in mem]
    def avg_pair(names):          # group strength: average correlation between every pair of members
        names = [x for x in names if x in col]
        if len(names) < 2: return None
        C = np.corrcoef(Z[:, [col[x] for x in names]].T); n = len(names)
        return round(float((C.sum() - n) / (n * (n - 1))), 2)
    for th, m in groups.items(): strength[th] = avg_pair(m + [x for _, x in ext.get(th, [])])
    for label, g in auto: strength[label] = avg_pair([x for _, x in g])
    print(f"co-movement: window {win[0]}..{coh_anchor}, {len(univ)} stocks, {len(liquid)} liquid, "
          f"{sum(len(v) for v in ext.values())} auto-added to baskets, {len(auto)} auto groups", file=sys.stderr)
except Exception as e:   # the portal still works with the core baskets only
    print(f"warning: co-movement step skipped: {e}", file=sys.stderr)

theme_of = defaultdict(list)
for cat, th, etfs, mem in T:
    for s in mem.split(): theme_of[s].append(th)
for th, v in ext.items():
    for _, s in v: theme_of[s].append(th)
for label, g in auto:
    for _, s in g: theme_of[s].append(label)

def compound(series, n):
    """return over the last n sessions, compounding Nasdaq's daily % change (split-safe)."""
    if len(series) < n + 1: return None
    acc = 1.0
    for i in range(len(series) - n, len(series)):
        p, pct, _ = series[i]
        p0 = series[i - 1][0]
        if pct is None:
            if not p or not p0: return None
            pct = (p / p0 - 1) * 100
        acc *= 1 + pct / 100
    return (acc - 1) * 100

def adj_closes(series):
    """closes adjusted back from today's price with each day's % change (split-safe), oldest first; None past a gap."""
    a = [None] * len(series); a[-1] = series[-1][0]
    for i in range(len(series) - 1, 0, -1):
        p, pct, _ = series[i]; p0 = series[i - 1][0]
        r = 1 + pct / 100 if pct is not None else (p / p0 if p and p0 else None)
        if not r or r <= 0: break
        a[i - 1] = a[i] / r
    return a

def dollar_vol(series, n):
    v = [p * vv for (p, _, vv) in series[-(n + 2):] if p and vv][-n:]
    return sum(v) / len(v) if len(v) >= n - 2 else None

def adr_pct(sym):
    x = [hl[sym][d] for d in sessions[-ADR_N:] if d in hl.get(sym, {})]
    return sum(h / l - 1 for h, l in x) / len(x) * 100 if len(x) >= ADR_N - 5 else None

def snap_val(sym, key):   # the user's 4:10 PM snapshot computes these from a year of Yahoo bars, today included
    r = snapf.get(sym) if snapf and snapf.get("_sess") == asof else None
    v = (r or {}).get(key)
    return float(v) if isinstance(v, (int, float)) else None

EXN = {"nasdaq": "NASDAQ", "nyse": "NYSE", "amex": "AMEX"}
out = []
for s, r in latest.items():
    if s not in hist: continue
    stale = asof not in hist[s]
    # the newest day came from a source that skips this listing (e.g. Yahoo file is US-only): keep the
    # stock, but show no change figures until the next file has it
    if stale and not (asof in extra and any(x in hist[s] for x in sessions[-3:])): continue
    mcap = num(r["marketCap"]) or 0
    if mcap < MIN_MCAP or not is_common(s, r["name"]): continue
    ser = [hist[s][d] for d in sessions if d in hist[s]]
    price, pct1, vol = ser[-1]
    if not price: continue
    vols = [v for (_, _, v) in ser[-AVG_N:] if v is not None]
    avg = sum(vols) / len(vols) if len(vols) >= 10 else None
    prev20 = [v for (_, _, v) in ser[-21:-1] if v is not None]
    avg20 = sum(prev20) / len(prev20) if len(prev20) >= 10 else None
    if s in fd: sec, ind = fd[s]["sector"], fd[s]["industry"]
    elif votes[r["industry"]]: sec, ind = votes[r["industry"]].most_common(1)[0][0]
    else: sec, ind = (r["sector"] or "Other"), (r["industry"] or "Other")
    idx = [n for n, ok in (("S&P 500", s in sp500), ("Nasdaq-100", s in NDX)) if ok]
    c1 = pct1 if pct1 is not None else compound(ser, 1)
    if stale: c1 = None
    adj = adj_closes(ser)
    sma = snap_val(s, "sma200")
    if sma is None and len(adj) >= SMA_N and None not in adj[-SMA_N:] and not stale: sma = sum(adj[-SMA_N:]) / SMA_N
    above = None if sma is None or stale else price > sma
    adr = snap_val(s, "adr_20")
    if adr is None: adr = adr_pct(s)
    dv10 = snap_val(s, "dvol_10") or dollar_vol(ser, 10)
    dv20 = snap_val(s, "dvol_20") or dollar_vol(ser, 20)
    # a filter with no data for this stock (e.g. no ADR% for a foreign listing yet) doesn't drop it
    g = bool(c1 is not None and c1 >= G_PCT and mcap >= G_MCAP and avg is not None and avg >= G_VOL and price >= G_PRICE
             and (adr is None or adr >= G_ADR) and (dv20 is None or dv20 >= G_DVOL) and above is not False)
    rd = lambda x, k=2: None if x is None else round(x, k)
    out.append({
        "symbol": s, "name": clean_name(r["name"]), "exchange": EXN[r["_ex"]],
        "tv_symbol": EXN[r["_ex"]] + ":" + s.replace("/", "."),
        "price": rd(price), "chg_1d": rd(c1), "chg_1w": None if stale else rd(compound(ser, 5)),
        "chg_1m": None if stale else rd(compound(ser, 21)), "chg_3m": None if stale else rd(compound(ser, M3)),
        "mcap_b": rd(mcap / 1e9), "volume": None if vol is None else int(vol), "avg_vol_30d": None if avg is None else int(avg),
        "rel_vol": rd(vol / avg20) if (avg20 and vol) else None,   # full day vs the previous 20 sessions' average
        "adr_20": rd(adr), "dvol_10_m": rd(dv10 / 1e6, 1) if dv10 else None, "dvol_20_m": rd(dv20 / 1e6, 1) if dv20 else None,
        "sma200": rd(sma), "above_200": above, "vs_200": rd((price / sma - 1) * 100, 1) if sma and not stale else None,
        "sector": sec, "industry": ind, "industry_detail": r["industry"] or "Other",
        "themes": " | ".join(theme_of.get(s, [])), "index": " | ".join(idx), "gainer": g,
        # a one-day move of 50%+ inside the 3M window is often a split or spin-off: check the chart
        "big_move": any(x[1] is not None and abs(x[1]) >= 50 for x in ser[-M3:]),
        "no_new_price": stale,
        # closes the 5-minute live job compares today's price with (next session's 1W / 1M / 3M)
        "ref_1w": None if stale or len(adj) < 5 else rd(adj[-5], 4),
        "ref_1m": None if stale or len(adj) < 21 else rd(adj[-21], 4),
        "ref_3m": None if stale or len(adj) < M3 else rd(adj[-M3], 4),
    })
out.sort(key=lambda x: -x["mcap_b"])

syms = {o["symbol"] for o in out}
themes = [{"category": c, "theme": th, "kind": "core", "etfs": " ".join(e.split()),
           "members": " ".join(m.split()), "n_members": len(m.split()),
           "ext": " ".join(x for _, x in sorted(ext.get(th, []), reverse=True)),
           "scores": " ".join(f"{x}:{scores[(th, x)]}" for x in m.split() if (th, x) in scores)
                     + "".join(f" {x}:{sc}" for sc, x in sorted(ext.get(th, []), reverse=True)),
           "strength": strength.get(th),
           "weak": " ".join(f"{x}:{scores[(th, x)]}" for x in m.split() if (th, x) in scores and scores[(th, x)] < 0.4),
           "missing": " ".join(x for x in m.split() if x not in syms)} for c, th, e, m in T]
themes += [{"category": "Auto groups", "theme": label, "kind": "auto", "etfs": "",
            "members": " ".join(x for _, x in g), "n_members": len(g), "ext": "",
            "scores": " ".join(f"{x}:{sc}" for sc, x in g), "strength": strength.get(label), "weak": "",
            "missing": ""} for label, g in auto]

json.dump(out, open(os.path.join(OUT, "stocks.json"), "w"), separators=(",", ":"))
json.dump(themes, open(os.path.join(OUT, "themes.json"), "w"), separators=(",", ":"))
json.dump([{"asof": str(asof), "sessions": len(sessions), "first_session": str(sessions[0]),
           "stocks": len(out), "gainers": sum(o["gainer"] for o in out),
           "latest_source": kind_of[asof], "chain_breaks": " ".join(breaks),
           "groups_as_of": str(coh_anchor) if coh_anchor else "", "auto_added": sum(len(v) for v in ext.values()),
           "auto_groups": len(auto),
           "adr_source": ("your close snapshot" if snapf and snapf.get("_sess") == asof else "Yahoo daily highs/lows (US-domiciled stocks)"),
           "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}],
          open(os.path.join(OUT, "build.json"), "w"))
print(json.dumps({"asof": str(asof), "latest_source": kind_of[asof], "chain_breaks": breaks,
                  "sessions": len(sessions), "stocks": len(out),
                  "gainers": sum(o["gainer"] for o in out),
                  "theme_missing": {t["theme"]: t["missing"] for t in themes if t["missing"]}}))

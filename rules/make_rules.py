#!/usr/bin/env python3
"""The scanner rules as a spreadsheet and Markdown tables: rules/scanner_rules.xlsx and rules/SCANNER_RULES.md.

  python3 rules/make_rules.py

Any rule change updates this file and re-runs it in the same commit (HANDOFF.md). The liquidity numbers come from
scanner/settings.json; the rest is written here in plain words, from scanner/launch.py, scanner/run.py, radar/ and the
morning grading instructions.
"""
import json, os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SET = json.load(open(os.path.join(ROOT, "scanner", "settings.json")))
ST, LA = SET["standard"], SET["launch"]
LAUNCH_LIQ = (f"Price ${LA['min_price']}+, 20-day avg $ volume ${LA['min_dollar_vol_20d_millions']}M+, "
              f"{LA['min_avg_vol_20d'] / 1000:.0f}K+ shares a day (20-day avg), ADR {LA['min_adr']}%+")
WATCH_LIQ = (f"Price ${ST['min_price']}+, market cap ${ST['min_mcap'] / 1e6:.0f}M+, 20-day avg volume "
             f"{ST['min_avg_vol_20d'] / 1000:.0f}K+ shares and ${ST['min_dollar_vol_20d_millions']}M+ a day (20-day), ADR "
             f"{ST['min_adr']}%+" + (", close above the 50 EMA" if ST.get("above_ema50") else "")
             + (f", {ST['min_pct_above_52w_low']}%+ above the 52-week low" if ST.get("min_pct_above_52w_low") else ""))
SHEETS = {
"L1 Launch must-pass": (["Rule", "Requirement", "Notes"], [
 ["Liquid", LAUNCH_LIQ, "Your settings (scanner/settings.json, 'launch')"],
 ["History", "200+ sessions", "A newer listing needs 60+ sessions and uses its average close since listing as the 200 SMA"],
 ["Above 52-week low", "Close 30%+ above the 52-week low", "-"],
 ["200 SMA", "Close ABOVE the 200 SMA; the day before at most 28% above it (power day: up to 50%)", "Laggards are the exception: they close UNDER it"],
 ["No repeats", "No other launch in the previous 20 sessions", "Unless the stock closed under its 21 EMA since then"],
]),
"L2 Launch types": (["Type", "Gap", "Day's move", "Volume (x 20-day avg)", "Must clear 1-month (20-day) high?", "Other conditions", "Shown as"], [
 ["1. Launch (regular)", "Opened up (any gap)", "+5%+, closes in the top half of the range", "1.5x+", "No (it is a grade ingredient: 'Base BO')", "-", "Type: Launch"],
 ["2. Power day", "8%+", "+10%+", "4x+", "YES (since Nov 2, 2026)", "May start up to 50% over the 200 SMA; closing in the lower half but holding half the gap = 'faded'", "Type: Power day"],
 ["3. Catalyst", "5%+", "Closes up (can be under +5% or below the top half)", "2x+", "YES (by the candle bodies)", "Earnings that day / the evening before, or an A/B pre-market grade; closes over the prior day's high", "Type: Catalyst"],
 ["4. Reversal", "Opened DOWN", "+8%+, closes in the top half", "2x+", "YES", "-", "Type: Reversal"],
 ["5. Delayed", "-", "A regular launch", "-", "No", "Within 10 sessions after a faded 3%+ gap on 3x+ volume that held its base; graded with that gap day", "Type: Delayed"],
 ["6. Follower", "-", "+2%+, closes in the top half", "2x+", "YES (20-day high)", "Within 10 sessions of an A/B launch by another stock in its theme", "Type: Follower (follows XYZ)"],
 ["7. Laggard", "Opened up", "+5%+, closes in the top half", "2x+", "YES (since Nov 2, 2026)", "Closes UNDER the 200 SMA; MUST have earnings or an A/B news grade that day; moves to Launches after 5 closes in a row over the 200 SMA", "Launch laggards tab; then 'from laggards' on Launches"],
 ["Your pick", "-", "-", "-", "-", "Added with the Follow button; followed like a launch, no launch day to grade", "Type: Your pick"],
]),
"L3 Launch grade": (["Grade", "Rule"], [
 ["Ingredients", "Volume 3x+ · gap 3%+ · base breakout (close over the previous 20 days' high) · a 10%+ day"],
 ["A+", "Volume 3x+, a 6%+ gap and a base breakout, jumping from under the 200 SMA to over it ('go day'). Laggards top out at A (they close under the 200 SMA)"],
 ["A", "Volume 3x+ and a base breakout, with a 3%+ gap or a 10%+ day"],
 ["B", "Two of the four ingredients"],
 ["C", "The rest"],
]),
"L4 Breakout grade": (["Grade", "Rule", "2-year history (ran 10%+ / 20%+ in 20 days)"], [
 ["A", "Early breakout (1st or 2nd since the launch, within 50 sessions) in a Leading theme, volume building the 5 days before", "62% / 35%"],
 ["B", "Early plus one of those two", "51% / 24%"],
 ["C", "The rest", "40% / 15%"],
]),
"L5 Off the list": (["Reason", "Rule"], [
 ["50 EMA", "3 closes in a row under the 50 EMA (after 2 it waits in the 50 EMA undercut list for the reclaim)"],
 ["Stale", "62 sessions from its highest point without a new high"],
 ["ADR", "ADR (20 days) drops under 3.2%"],
 ["Removed", "You removed it with the X button"],
]),
"L6 Tags": (["Tag", "Meaning"], [
 ["earnings", "Launched on its earnings report (that day or the evening before)"],
 ["news", "The pre-market grading gave it an A or B that morning"],
 ["faded", "Power day that closed in the lower half of its range but held half its gap"],
 ["cleared 1/3/6-mo base", "The biggest base the launch day closed over (by the candle bodies)"],
 ["neglected", "40+ days since its high, or a 25%+ correction"],
 ["lone wolf", "None of its groups has trended since the launch"],
 ["tight x2", "2+ tight days just under the buy point"],
 ["retest held", "Pulled back to the broken base top and closed back over it"],
 ["gap out of base", "Opened over last night's base high"],
 ["from laggards", "Launched under the 200 SMA, then 5 closes in a row over it: moved to Launches"],
 ["Resistance column", "Overhead 3/6/9-month and 52-week highs past the buy point, nearest first, with % away"],
]),
"L7 Live lists": (["What", "When", "Rule"], [
 ["Launching today", "Every 5 min, 9:30 AM-4:00 PM ET", "Watch list stocks meeting the launch rules on live prices (volume = pace for the time of day)"],
 ["Laggards launching today", "Every 5 min, 9:30 AM-4:00 PM ET", "Under the 200 SMA, earnings/A-B news today, opened up, +5%+, 2x+ volume pace, over its 1-month high"],
 ["1-minute checks", "9:31 AM-12:00 PM and 3:00-4:00 PM ET", "Big gap-ups (catalyst gap, power day, A+/A launch) and the followed launches' breakouts"],
 ["Breakout alert", "Every check", "A followed launch trading over its buy point on 1x+ volume pace, after closing under it the day before"],
 ["Touched & back under", "Every check", "Traded over the buy point (today's high) but is back under it: a heads-up, not a breakout"],
 ["Table update", "After the close (scan about 4:40 PM ET)", "Launches that held at the close are added, dated that day"],
]),
}


SHEETS.update({
"W1 Watchlist lists": (["List", "Gets on", "Leaves on", "Sections"], [
 ["Every list needs", WATCH_LIQ, "-", "-"],
 ["1-EP/GAP", "Gap up of more than 5% at the open with relative volume 2.5x+ (no 200 SMA rule)", "2 closes in a row below the 50 EMA, or 15 trading days without reaching 3-SETUPS", "The gap day (a new gap moves it to the newer section)"],
 ["1-UPDAY", "Up 4%+ on the day with relative volume 1x+ (no 200 SMA rule)", "2 closes in a row below the 50 EMA, a close below the up day's low, or 15 trading days without reaching 3-SETUPS", "The up day"],
 ["2-POOL", "First close back above the 50 EMA after 2+ closes below it; or, refreshed every Friday, momentum leaders: +10% in 1 week, +25% in 1 month, +50% in 3 months, or +50% in 6 months (that one also above the 200 SMA and 50%+ over its 52-week low)", "2 closes in a row below the 50 EMA; at the Friday refresh, a close below the 200 SMA or no longer liquid", "50 EMA reclaim / Momentum"],
 ["3-SETUPS", "A name from 1-EP/GAP, 1-UPDAY or 2-POOL that the Launches engine reads as a setup; ADR 4%+ to come on", "2 closes in a row under the 50 EMA, 62 sessions without a new high, ADR under 3.2%, or your X", "Triggered today / Ready (trigger within 0.7 ADR over the close, in a base of 5+ days or tight 2+ days under it) / Setting up (flag forming, 21 EMA pullback set up, near a retest)"],
 ["Other screens (settings)", "Daily tightness: 40%+ over the 52-week low, within 30% of the 52-week high, volume 20%+ under its 30-day average, range at most 0.8x the 10-day average, 3 tight days in the last 5. Pullback to 21 EMA / 50 EMA: within 3% over that EMA, above the 200 SMA, 21 EMA over 50 EMA", "-", "-"],
]),
"W2 Watchlist grade": (["Grade", "Rule"], [
 ["Trend first", "10 EMA above 21 EMA above 50 EMA, price above the 50 EMA and the 200-day SMA; otherwise no grade (-)"],
 ["A+", "Last pullback from the 20-day high was 10-15%"],
 ["A", "A pullback of up to 20% (other than 10-15%)"],
 ["B", "A pullback of 20-30%, only for stocks with an ADR of 8%+"],
 ["Note", "This grades the trend and the last pullback; the Launches tab grades the launch day itself, so the same stock can grade differently"],
]),
"B1 Buy points (triggers)": (["Trigger", "What it is / requirements", "Buy point", "New leg?"], [
 ["Base top", "Highest high of the last ~6 months, at least 5 sessions old, with a pullback of 1.25+ of the stock's own ADRs from it", "The base top. Close more than 0.5% over it on 1x+ volume = base breakout. Within 0.5% = breakout with caution (follow-through within 3 sessions: opens over the day before's close and closes 0.5%+ over the top)", "Yes"],
 ["Bull flag (trendline)", "Top at least a 1-month high after a run of 4+ ADRs; 5+ day base with 4+ pullback days, 1.25-4 ADRs deep, 3+ lower highs in a descending channel; volume at or under 1.1x the 20-day average; riding the 10 or 21 EMA (3+ days within 1 ADR); never closes more than 0.5 ADR under the 21 EMA; no violent drop", "Tomorrow's value of the falling line along its highs; entry = close over the line and the 10 & 21 EMA", "No (entry inside the base)"],
 ["Bull pennant (trendline)", "Same as the bull flag after the pole, but converging: lower highs and higher lows; volume after its first low at or under 1.1x average", "The falling upper line", "No (entry inside the base)"],
 ["Pop out of the consolidation", "Consolidation 1+ ADR under the top; volume dried up (5-day at or under 0.85x the 50-day); surfing the 10 & 21 EMA (closes within 1 ADR) above the 50 EMA; then a tight candle (range at or under 0.8 ADR, body at or under 0.5 ADR)", "Next day opens above that candle's open and close and above the rising 10 & 21 EMA (the open is the trigger); once per base", "No"],
 ["21 EMA retest", "5+ days into the base and 1.25+ ADRs off its high; controlled pullback (no advance the 3 days before, closes held over the 21 EMA)", "Low goes under the 21 EMA and under the open, close comes back over it in the upper half of the day; once per pullback", "No"],
 ["Retest held", "Once per breakout: after a real pullback, the low at the broken base top (bodies or wicks)", "Close back over the top and the 21 EMA (holding over the 10 EMA, or the low tested the 21 EMA and reclaimed it)", "No"],
 ["Breakout undercut & reclaim", "After a breakout, 2+ closes back under its level while holding over the 50 EMA", "The close back over the level, within 5 sessions", "No"],
 ["21 EMA undercut & reclaim", "2 closes under the 21 EMA by less than 0.5 ADR", "The close back over the 21 EMA (strong signal)", "No"],
 ["Push out of the 21 EMA", "After a retest, a push out of the 21 EMA with a gap (not while still under a flag's falling line)", "The gap open", "No"],
 ["Double breakout", "The base top and a falling line inside the base broken the same day", "The base top", "Yes"],
 ["3rd try (ascending triangle)", "1st try = the base high, a 2nd try within 0.25 ADR of it after a real pullback, then a shallower pullback (higher lows)", "The base high on the 3rd try", "Yes"],
 ["Gap out of base", "Opens over last night's base high (base top or a pattern pivot); needs ADR 4%+, 600K+ shares a day", "Over the 1- or 5-minute opening range high, stop its low; out at 9:50 if the volume pace isn't 2x", "-"],
 ["MSF pattern pivot", "Your MSF engine's pattern (High tight flag, Flat base, Cup with handle, ...)", "The pattern's pivot", "Yes"],
 ["Which one is shown", "The nearest trigger above the price", "-", "-"],
 ["Exit signal", "The first close below the 21 EMA", "-", "-"],
]),
"B2 Legs & status": (["Item", "Rule"], [
 ["Leg 1", "The launch, when it closed out of its base or cleared at least its 1-month base (by the bodies); otherwise leg 0 (in base) until the first breakout"],
 ["Later legs", "A close out of a base (more than 0.5% over its top) or out of a flag at the highs; one leg per base; breakouts a few days apart are one leg"],
 ["Late", "Leg 4+ (breakouts got worse leg by leg in the 2-year test)"],
 ["New run", "A breakout after a rest of 40+ sessions without a new high starts again at leg 1"],
 ["Status: In the base", "Under the top, no close above the level its leg broke out of, or 1.25+ ADRs off its latest high"],
 ["Status: Consolidation (resting)", "Surfing the 10 & 21 EMA on dry volume: closes within 1 ADR of both, above the 50 EMA, bodies 0.5 ADR or less, 5-day volume 0.85x or less of the 50-day"],
 ["Status: others", "Tight under the buy point, breakout, running, retest that held"],
 ["tight x2", "2+ tight days just under the buy point (within 1 ADR, bodies 0.5 ADR or less, sideways)"],
 ["50 EMA undercut list", "2 closes in a row under the 50 EMA: waits there for the reclaim next session; a 3rd close under takes it off"],
]),
"P1 Pre-market grading": (["Item", "Rule"], [
 ["When", "Starts 8:50 AM ET on weekdays; final price check at 8:57; posted by 9:05. If it starts late it still grades everything"],
 ["Which gappers", "Gap of 5%+ (up or down) at the latest pre-market price; market cap $700M+, 20-day avg volume 700K+, 20-day avg $ volume $20M+, ADR 3%+"],
 ["How many graded", "Top 8 gap-ups and top 4 gap-downs by pre-market $ volume; the rest show ungraded under Show all"],
 ["Prices", "Newest of Yahoo's 5-minute bars, Yahoo's live pre-market quote and Alpaca (about 15 min behind); pre-market volume from Alpaca, about 15 minutes behind"],
 ["Searches per stock", "'Why is <company> stock moving today'; the company's own news / 8-K; for asset-driven companies (crypto treasuries, miners, holding companies, single-drug biotechs) the asset's news too"],
 ["Reliable sources only", "Facts only from primary sources (company release, SEC filing, exchange/regulator notice, earnings release or call) or major outlets (Reuters, Bloomberg, WSJ/Barron's/MarketWatch, FT, CNBC, AP). Social media, crypto/flash sites, aggregators, blogs and AI summaries = rumor: C at best, F if the move rests only on it"],
 ["No hindsight", "Graded only from the news as it stood before the open, not from price action"],
 ["Report", "Phone notification with the save time, 'prices as of' time, counts and A/B tickers; PRICES STALE if prices are 15+ minutes old"],
]),
"P2 Gap grades": (["Direction", "Grade", "Meaning"], [
 ["Gap-up", "A", "Real fundamental change: beat with raised guidance or clear growth acceleration, FDA approval, signed takeover at a premium, signed transformational contract, confirmed inflection 7+"],
 ["Gap-up", "B", "Decent: meaningful contract or partnership, beat-and-raise with modest growth, early turnaround (inflection 4-6), index addition"],
 ["Gap-up", "C", "Weak: analyst upgrade, sympathy, hype, talks/rumors with nothing signed, social-media posts or unconfirmed reports, no clear news"],
 ["Gap-up", "F", "Warning: offering/ATM/convertible or other dilution, promotional release, reverse split, unconfirmed news, going-concern or delisting issues"],
 ["Gap-down", "A", "Serious damage: guidance cut or withdrawn, big miss with weak outlook, lost major customer, failed trial, leadership ousted, accounting or fraud"],
 ["Gap-down", "B", "Meaningful but contained: modest miss, cautious guide, offering or dilution, one-off charge, credible competitive threat"],
 ["Gap-down", "C", "Weak or no real news: downgrade, sympathy, macro, strong report sold on valuation, unconfirmed reports (possible overreaction)"],
 ["Both", "Inflection 1-10", "Turnaround, Acceleration, New business, Margin, Deterioration or None (0); scored on size and how confirmed"],
]),
"P3 Pre-market scanner": (["Filter", "Your default"], [
 ["Direction", "Gap ups"], ["Pre-market change", "0.5% to 5%"], ["Price", "$5+"], ["Market cap", "$0.7B+"], ["Avg volume (20D)", "600K+"],
 ["Price x avg volume", "$20M+"], ["ADR", "4%+"], ["52-week low", "30%+ below price"], ["Above 200-day SMA", "off"], ["Above 50-day EMA", "off"],
 ["Updates", "Every 5 minutes, 7:00-9:29 AM ET"],
]),
"G1 Gainers filter": (["Filter", "Your default"], [
 ["Direction", "Gainers"], ["Day's change", "4%+"], ["Price", "$5+"], ["ADR", "3.5%+"], ["$ volume", "$30M+ (20-day)"],
 ["Above 200 SMA", "on"], ["Above 50 EMA", "off"], ["Market cap", "$0.7B+"], ["Avg volume (20D)", "700K+"],
]),
"A1 Alerts": (["Alert", "When it fires", "Checked"], [
 ["Pre-market grades", "The morning's graded gappers", "About 9:05 AM ET"],
 ["Early heads-up", "A 5%+ gap with a catalyst-gap / power-day / launch shape, before the volume can be read", "9:31-9:34, every minute"],
 ["Power day", "Volume pace 4x+, 8%+ gap, up 10%+, over its 1-month high, above the 200 SMA (at most 50% over it)", "1-minute and 5-minute checks"],
 ["Catalyst gap", "A neglected stock (under its 50 EMA or 200 SMA at the last close) gaps 5%+ on earnings or news with pace 3x+ and trades above both", "1-minute and 5-minute checks"],
 ["Catalyst 2nd trigger", "After a catalyst gap that hadn't cleared its base high: the base high cleared", "Same"],
 ["A+/A launch", "Off the watch list, graded like Launching today", "Same"],
 ["Laggard launch", "Under the 200 SMA, earnings or A/B news today, opened up, up 5%+, pace 2x+, over its 1-month high", "Same"],
 ["Gapping to buy point", "A followed launch gaps 2%+ on 1.2x+ pace to within 2% under its buy point", "Every check"],
 ["Breakout (A/B/C)", "A followed launch trades over its buy point on 1x+ pace after closing under it", "1-minute in the morning and last hour, else 5-minute"],
 ["Touched & back under", "Traded over the buy point since the last check but is back under it", "Every check"],
 ["Confirmation", "In the 3 sessions after a base breakout, opens and trades above the base top on 2x+ pace", "Every check"],
 ["Pop / gap out of base", "The pop out of the consolidation; an open over last night's base high", "From the open"],
 ["Retest zone / hold", "Pulls into the retest zone of its last breakout; from 3:45 PM, holding into the close", "Every check"],
 ["After the close", "Tight closes under a buy point, a retest of a broken base top that held; 3-SETUPS Ready list to the phone", "After the 4:40 PM scan"],
 ["Rules", "Each stock and kind once a day; phone via ntfy, desktop pop-ups while the portal page is open", "-"],
]),
})

SHEETS.update({
"L8 Groups & themes": (["Item", "Rule"], [
 ["Group", "Each of the stock's themes on the portal (or its industry when it has none), and one level up its area (AI & Semis, Software, Energy... or its sector)"],
 ["Leading", "60%+ of the group's members close above their 50 EMA and its median 1-month change is +8% or more"],
 ["Turning up", "Half or more of the members close above their 21 EMA and its median 1-week change is positive"],
 ["Not trending", "Neither of the above"],
 ["Theme then -> now", "The group's status on the launch day and today; 'since' = the first day from the launch it was trending (Turning up or Leading)"],
 ["Lone wolf", "None of its groups has trended since the launch"],
 ["Theme confirmed (2-year launch test)", "Its theme turned up (Turning up or Leading) after the launch: A+ launches then ran 20%+ 65% of the time vs 52% for other A's"],
 ["Breakout grade", "A Leading theme counts toward an A/B breakout; Turning up did no better than not trending in the 2-year test"],
]),
"L9 Live watch list": (["Item", "Rule"], [
 ["Universe", f"Every US stock with a market cap of ${ST['min_mcap'] / 1e6:.0f}M+ (Nasdaq's list; 2 years of daily bars)"],
 ["Liquid", LAUNCH_LIQ],
 ["History", "200+ sessions (60+ for a new listing)"],
 ["200 SMA range", "From 60% under to 50% over its 200 SMA (28-50% over: power days only; under it: laggards or once it trades back over)"],
 ["Not launched", "No launch in the last 20 sessions (those are followed on the Launches list)"],
 ["Rebuilt", "Every evening at the 4:40 PM scan"],
 ["5-minute checks", "Live prices for all ~3,300 stocks (tables); the launch and laggard rules on the watch list"],
 ["1-minute checks", "9:31-12:00 and 3:00-4:00: the watch list plus Launches, Launch laggards and the 50 EMA undercut list"],
]),
"O1 Open items": (["Item", "Status"], [
 ["Momentum cutoff", "Coded but OFF (L['max_run_pct'] = 0): no buy points once the stock has run 300%+ from its momentum start (option A) or 300%+ and 140%+ over the 200 SMA (option B). Your decision"],
 ["'No reset yet' tag", "Offered; may be replaced by the momentum cutoff"],
 ["Retest needs the 10/21 EMA at the level", "Offered, not decided"],
 ["Bull flag trigger on the higher of the line and the day before's high", "Offered, not decided"],
]),
})
def _examples():
    rows = []
    for ln in open(os.path.join(ROOT, "tools", "examples.txt")):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        body, _, note = ln.partition("#")
        f = body.split()
        if len(f) >= 4:
            rows.append([f[0], f[1], f[2], f[3], note.strip() or "-"])
    return rows
SHEETS["X1 Agreed examples"] = (["Ticker", "From", "To", "Launch / pick", "What you agreed"], _examples())

SHEETS = dict(sorted(SHEETS.items(), key=lambda kv: ("LWBPGAOX".index(kv[0][0]), kv[0])))
wb = Workbook(); wb.remove(wb.active)
hdr_fill = PatternFill("solid", fgColor="1F3864"); alt = PatternFill("solid", fgColor="EEF2F8")
thin = Side(style="thin", color="C8CED8"); bd = Border(top=thin, bottom=thin, left=thin, right=thin)
for name, (cols, rows) in SHEETS.items():
    ws = wb.create_sheet(name[:31])
    ws.append(cols)
    for r in rows: ws.append(r)
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True, color="FFFFFF", size=11); c.fill = hdr_fill
        c.alignment = Alignment(vertical="center", wrap_text=True); c.border = bd
    for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
        for j, c in enumerate(row):
            c.font = Font(name="Arial", size=10, bold=(j == 0)); c.alignment = Alignment(vertical="top", wrap_text=True); c.border = bd
            if i % 2 == 0: c.fill = alt
    for j, col in enumerate(cols, start=1):
        longest = max(len(str(x)) for x in [col] + [r[j - 1] for r in rows])
        ws.column_dimensions[get_column_letter(j)].width = min(max(14, longest * 0.9), 60)
    ws.freeze_panes = "A2"; ws.row_dimensions[1].height = 30
info = wb.create_sheet("About", 0)
for line in ["Theme & Group Radar: scanner rules", "As of Nov 2, 2026. Source of truth: scanner/launch.py, scanner/settings.json, radar/ and the morning grading instructions.",
             "L = Launches (L1-L9) · W = Watchlist (W1-W2) · B = Buy points, legs & status (B1-B2) · P = Pre-market (P1-P3) · G = Gainers (G1) · A = Alerts (A1) · O = Open items · X = Agreed examples",
             "Regenerate with: python3 rules/make_rules.py (any rule change updates it in the same commit)"]:
    info.append([line])
info["A1"].font = Font(name="Arial", bold=True, size=14)
for c in ("A2", "A3", "A4"): info[c].font = Font(name="Arial", size=10)
info.column_dimensions["A"].width = 110
XLSX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'scanner_rules.xlsx')
MD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'SCANNER_RULES.md')
wb.save(XLSX)

# the same tables as Markdown
md = ["# Scanner rules", "", "As of Nov 2, 2026. Source of truth: `scanner/launch.py`, `scanner/settings.json`, `radar/` and the morning grading instructions. Spreadsheet version: `rules/scanner_rules.xlsx`.", ""]
for name, (cols, rows) in SHEETS.items():
    md += ["## " + name.split(" ", 1)[1], "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join(str(x).replace("|", "/") for x in r) + " |" for r in rows] + [""]
open(MD, "w").write("\n".join(md))

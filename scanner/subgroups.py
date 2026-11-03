#!/usr/bin/env python3
"""Named sub-groups by what the companies do (the user, Nov 3 2026: "find really nice groups that move together and
belong to the same category"). Base: Yahoo's industry (143 of them, e.g. "Banks - Regional", "Oil & Gas Midstream");
the still-big ones are split by the business description:
  Biotechnology        gene & cell therapy, RNA medicines, oncology, neuro / psychiatry, immunology & inflammation,
                       obesity & metabolic / cardio, rare disease, infectious disease & vaccines, eye, other
  Banks - Regional     super-regional (US, $15B+), US regional & community, international
  Software - App/Infra cybersecurity, data & analytics / observability, developer & cloud platforms, fintech & payments
                       software, HR / payroll, vertical software (health, real estate, auto, insurance, government),
                       marketing & ad tech, design & engineering, crypto & bitcoin mining, AI & quantum
  Asset Management     alternative / private equity, BDC lenders, crypto treasuries, traditional asset managers
  python3 scanner/subgroups.py <profiles.json> <stocks.json> <out groups.json>   ->  {symbol: group name}
"""
import json, re, sys

RULES = {
    "Biotechnology": [
        ("Gene & Cell Therapy", r"gene therap|gene edit|crispr|base edit|aav|cell therap|car-t|car t|allogeneic|autologous|genetic medicine"),
        ("RNA Medicines", r"rnai|sirna|antisense|oligonucleotide|mrna|rna-targeted|rna therap"),
        ("Obesity & Metabolic", r"obesity|weight|glp-1|metabolic|diabetes|mash|nash|cardiometabolic|lipid|cardiovascular|hypertension"),
        ("Neuro & Psychiatry", r"neurolog|neuro|psychiatr|cns|alzheimer|parkinson|depress|epilep|schizophren|seizure|pain|sleep|migraine"),
        ("Oncology", r"cancer|oncolog|tumor|tumour|leukemia|lymphoma|myeloma|carcinoma|solid tumor"),
        ("Immunology & Inflammation", r"immunolog|inflammat|autoimmun|dermatolog|atopic|psoriasis|lupus|allerg|fibrosis|respiratory|asthma|copd"),
        ("Rare Disease", r"rare disease|rare genetic|orphan|ultra-rare|muscular dystrophy|duchenne|hemophilia"),
        ("Infectious Disease & Vaccines", r"vaccin|infectious|antiviral|antibiotic|antibacterial|antifungal|hiv|hepatitis|influenza|covid"),
        ("Eye Disease", r"ophthalm|retina|retinal|eye disease|glaucoma|macular"),
    ],
    "Software - Application": "SOFT", "Software - Infrastructure": "SOFT",
    "Asset Management": [
        ("Crypto Treasury & Digital Assets", r"bitcoin|ethereum|digital asset|crypto|blockchain|token"),
        ("BDC Lenders", r"business development compan|closed-end|middle market|direct lending|private credit|specialty finance"),
        ("Alternative Asset Managers", r"private equity|alternative asset|alternative investment|infrastructure fund|real asset|credit fund"),
    ],
}
SOFT = [
    ("Crypto & Bitcoin Mining", r"bitcoin|crypto|blockchain|digital asset|mining"),
    ("AI & Quantum", r"quantum|artificial intelligence|ai-powered|ai platform|generative ai|machine learning|gpu|ai infrastructure|high-performance comput"),
    ("Cybersecurity", r"security|cyber|identity|threat|zero trust|endpoint|firewall|fraud"),
    ("Data, Analytics & Observability", r"data|analytics|observability|monitoring|database|search"),
    ("Developer & Cloud Platforms", r"developer|devops|cloud platform|cloud infrastructure|api|open source|hosting|content delivery|edge"),
    ("Fintech & Payments Software", r"payment|banking|lending|financial institution|fintech|accounting|tax|spend|billing|invoice|treasury"),
    ("HR & Payroll Software", r"payroll|human capital|human resources|hr |workforce|employee|talent"),
    ("Vertical Software", r"healthcare|health care|hospital|pharmac|real estate|property|automotive|dealer|insurance|government|public sector|construction|restaurant|education|school|hospitality|legal"),
    ("Marketing & Ad Tech", r"marketing|advertis|customer engagement|commerce|e-commerce|sales|crm"),
    ("Design & Engineering Software", r"design|engineering|simulation|3d|cad|product lifecycle|creative"),
]
INTL = r"brazil|argentin|colombi|peru|chile|mexic|india|korea|japan|china|hong kong|spain|united kingdom|canada|puerto rico|bermuda|europe|panama"


def name_of(sym, prof, stock):
    ind = prof.get("industry") or stock.get("industry") or "Other"
    txt = (prof.get("about") or "").lower()
    if ind == "Banks - Regional":
        if re.search(INTL, txt[:300]):
            return "Banks - International"
        return "Banks - Super-Regional" if (stock.get("mcap_b") or 0) >= 15 else "Banks - US Regional & Community"
    rules = RULES.get(ind)
    if rules == "SOFT":
        rules = SOFT
    if rules:
        for nm, rx in rules:
            if re.search(rx, txt):
                return f"{ind.split(' - ')[0] if ind.startswith('Software') else ind}: {nm}" if not ind.startswith("Software") else f"Software: {nm}"
        return f"{ind}: other"
    return ind


def main():
    P = json.load(open(sys.argv[1]))["rows"]
    S = {r["symbol"]: r for r in json.load(open(sys.argv[2]))}
    out = {s: name_of(s, P.get(s, {}), S[s]) for s in S}
    json.dump(out, open(sys.argv[3], "w"), indent=0, sort_keys=True)


if __name__ == "__main__":
    main()

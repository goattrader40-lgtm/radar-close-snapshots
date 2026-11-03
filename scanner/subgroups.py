#!/usr/bin/env python3
"""Named groups by business line (the user, Nov 3 2026: "what moves together, business lines, how they are bonded in
stock market action"). Every stock gets ONE industry-level group:
  1. the hand list below, by what the company does (big buckets: biotech, software, banks, asset managers, brokers,
     crypto, AI hosting), checked later against how the stocks move together;
  2. otherwise Yahoo's industry (143 of them: "Oil & Gas Midstream", "Gold", "Restaurants", ...).
Themes on the portal stay as they are; these replace the 73 broad industries.

  python3 scanner/subgroups.py <profiles.json> <stocks.json> <out groups.json>   ->  {symbol: group}
"""
import json, sys

G = {
    # ---- biotech, by what the stock trades on
    "Biotech: Large-Cap Commercial": "VRTX REGN ARGX ONC GMAB INCY INSM EXEL ASND BBIO JAZZ",
    "Biotech: Oncology": "RVMD SMMT CGON COGT ERAS RLAY TNGX CELC ELVN IDYA IMNM RCUS XNCR ZYME LKFT SLS URGN NUVB TYRA NBTX ANL "
                         "AAPG KURA SNDX VSTM JANX IMTX IMCR CRVS ORIC CADL OLMA BLSM GERN AURA AVBP NVCT CBIO BCAX FTH MNPR PBYI PRLD "
                         "EIKN CTMX REPL INDP FENC ETRA RLMD IBRX",
    "Biotech: Radiopharma": "TLX AKTS DRTS",
    "Biotech: Cell Therapy": "LEGN IOVA ALLO AUTL KYTX SANA IMMX VCEL MESO CAPR PROK OBX",
    "Biotech: Gene Editing & Gene Therapy": "CRSP NTLA BEAM PRME EDIT SRPT KRYS QURE RGNX TSHA SLDB NGNE FDMT MGTX IRD PGEN",
    "Biotech: RNA Medicines": "ALNY ARWR IONS WVE SLN ADRX CTY ABUS DYN",
    "Biotech: Obesity & Cardiometabolic": "VKTX MDGL GPCR MBX KLRA ALT NAMS MLYS KARD BRVE CYTK LXRX SGMT IVA GALT MNKD RZLT VOGX "
                                         "SEPN CORT MAZE ENTX TECX",
    "Biotech: Immunology & Inflammation": "ROIV IMVT SYRE ABVX ORKA PTGX DNTH TGTX CLDX VERA AUPH ZBIO TRAX LYCA JBIO ALMS ODTX "
                                         "ANNX ATTO ACRS CLYM AGMB AVTX ZURA TRXB MLTX MANE ARQT DBVT SPRY VOR CTNM OMER NKTR",
    "Biotech: Protein Degraders": "KYMR NRIX ARVN CCCC GLUE",
    "Biotech: Neuro & Psychiatry": "AXSM PRAX XENE ACAD DFTX DNLI GHRS LBRX RAPP SPTX ANRO HELP MPLT OVID LTGO KRSA ALEC PRTA "
                                  "HRMY APMD BHVN TRVI ACHV",
    "Biotech: Rare Disease & Hematology": "BMRN RYTM MIRM PTCT TVTX EWTX SRRK PHVS IRON DSGN COAG DMRA RARE ZVRA PHAR XFOR AGIO "
                                         "PVLA IRLA RIGL AVLN VCRE GYRE DMAC INBX",
    "Biotech: Vaccines & Infectious Disease": "MRNA BNTX PCVX NVAX VALN VIR ADMA ASMB AVIR ENTA SABS CRMD",
    "Biotech: Eye Disease": "KOD BLTE TARS OCUL SGP OCS VRDN YDES SRZN",
    "Biotech: Royalties": "RPRX HALO LGND INVA ANAB",
    "Biotech: AI & Platform Drug Discovery": "RXRX ABSI GENB IAM ABCL OABI PBLS",
    "Bio Tools & Services": "TECH MRVI FTRE TWST DNA CAI",
    # ---- software
    "Software: Majors": "MSFT SAP CRM NOW ADBE INTU WDAY ADSK TEAM ROP",
    "AI Cloud & Data-Center Hosting": "ORCL CRWV IREN CIFR WULF CORZ HUT APLD NBIS GLXY WYFI SHAZ",
    "Software: AI Applications": "PLTR AI SOUN RZLV RZAI BRUN PATH BBAI INOD",
    "Quantum Computing": "QNT INFQ XNDU HQ IONQ RGTI QBTS QUBT IQMX PSQL",
    "Software: Cybersecurity": "PANW CRWD FTNT ZS OKTA CHKP S QLYS TENB RPD VRNS SAIL NTSK CVLT RBRK GEN MITK YOU CGNT CLBT TLS "
                               "ALLT BB OSPN ATEN RDWR RSKD NTCT",
    "Software: Cloud, Data & Observability": "SNOW DDOG MDB ESTC NTNX DT FROG GTLB NET FSLY AKAM DOCN TDC PD BLZE RXT TWLO BAND "
                                             "API FFIV AVPT",
    "Software: Web Presence & Domains": "GDDY VRSN WIX",
    "Software: Marketing & Ad Tech": "HUBS BRZE KVYO CXM SPT AMPL SMWB YEXT GTM ZETA RAMP DSP PUBM MNTN APPS IBTA",
    "Software: Collaboration & Communications": "FRSH ZM DOCU MNDY ASAN BOX DBX RNG FIVN EGHT OOMA NICE PEGA APPN",
    "Software: HR & Payroll": "ADP PAYX PAYC PCTY",
    "Software: Finance & Banking": "BILL BL WK VERX DFIN SSNC FICO QTWO NCNO ALKT ACIW",
    "Payments": "XYZ TOST CPAY WEX FOUR PAY PAYO FLYW DLO EEFT EVTC MQ RELY PAGS NYAX RPAY PSFE PRTH PAYS IIIV LSAK PAYP KSPI "
                "PYPL AFRM STNE",
    "Consumer Fintech": "CHYM DAVE PGY KPLT WLTH UPBD SOFI UPST",
    "Software: Vertical & Industry": "TYL GWRE CCC PCOR APPF MANH DSGX SPSC AGYS TTAN BLKB INTA LAW DCBO EVCM LSPD PAR DOX ALRM "
                                     "KARO AIOT IOT SABR CCSI VEEV",
    "Software: Design & Engineering": "CDNS SNPS PTC BSY FIG U PDFS MTLS",
    "Software: E-commerce Platforms": "SHOP VTEX GCT",
    "Consumer Apps & Ride-Hailing": "UBER LYFT GRAB DUOL GRND LIF YALA YMM VIA NAVN SRAD BSP YB",
    "Autonomous Driving & Robotaxi": "WRD ENRD AEVA",
    "IP Licensing": "IDCC ADEA",
    # ---- banks
    "Banks: US Money-Center": "JPM BAC C WFC",
    "Banks: Custody & Trust": "BNY STT NTRS",
    "Banks: Canada": "RY TD BMO BNS CM",
    "Banks: Europe": "HSBC SAN UBS BBVA ING BCS LYG DB NWG",
    "Banks: Japan & Korea": "MUFG SMFG MFG KB SHG WF",
    "Banks: India": "HDB IBN",
    "Banks: Latin America": "ITUB NU BBD BBDO BAP BCH BSAC AVAL IFS GGAL BMA BBAR INTR BLX AGBK",
    "Banks: US Super-Regional": "USB PNC TFC FITB MTB HBAN CFG FCNCA RF KEY EWBC PNFP",
    "Banks: Digital & Specialty": "AX TBBK CASH LOB CUBI ESQ",
    # ---- asset managers, brokers, exchanges
    "Alternative Asset Managers": "BX KKR APO ARES CG TPG BAM BN OWL HLNE GCMG PAX VINP",
    "BDC Lenders": "ARCC MAIN OBDC OTF GBDC FSK HTGC TSLX TRIN CSWC OCSL GSBD BBDC KBDC PSEC MFIC CGBD FDUS BCSF PFLT NMFC "
                   "SLRC GAIN NCDL GLAD TCPC CCAP CION",
    "Closed-End & CLO Funds": "OXLC CET GAB GAM RVT RMT BKT SOR ASA PS PSUS FSCO BTX",
    "Traditional Asset Managers": "BLK TROW BEN IVZ AMG FHI CNS APAM VCTR VRTS WT AAMI SEIC NOAH ALTI SII JHG",
    "Wealth & Retirement": "AMP RJF PFG CRBG EQH SCHW LPLA SF",
    "Wall Street Banks": "GS MS NMR",
    "Advisory & Mid-Market Banks": "EVR HLI PJT LAZ MC PIPR PWP LCLN JEF OPY BRBI",
    "Online Brokers": "HOOD IBKR FUTU TIGR ETOR BULL",
    "Exchanges & Trading": "CME ICE NDAQ CBOE MKTX TW VIRT BGC MRX SNEX MIAX",
    "Crypto Platforms": "COIN CRCL BLSH BTGO GEMI CSHR FIGR SECZ CD",
    "Crypto Treasuries": "MSTR BMNR SBET ASST PURR FWDI XXI",
    "Bitcoin Miners": "MARA RIOT CLSK HIVE ABTC BTDR IOND",
    # ---- fixes after the first co-movement check (Nov 3 2026)
    "Insurtech": "LMND ROOT HIPO PRCH TRUP",
    "Insurance: Florida Homeowners": "HCI UVE HRTG ACIC AII SLDE",
    "Utilities - Latin America & Asia": "CEPU CIG EDN ELPC KEP SBS ENIC",
    "eVTOL & Air Mobility": "JOBY ACHR BETA",
    "Solar": "DQ",
    "Land & Royalty": "TPL LB",
    "Preferred & Duplicate Shares": "ZIONP CDZIP FRMEP WAFDP",
    # ---- tech, split finest (the user, Nov 3 2026: "top priority should be tech, where the momentum is")
    "Semis: AI Accelerators & CPUs": "NVDA AMD INTC ARM AVGO CBRS",
    "Semis: AI Connectivity & Interconnect": "ALAB CRDO MRVL RMBS MTSI SMTC MXL AIP",
    "Memory & Storage Chips": "MU SKHY SNDK WDC STX SIMO MRAM",
    "Semis: Foundry": "TSM UMC GFS TSEM",
    "Semis: Analog, Auto & Power": "TXN ADI MCHP NXPI ON MPWR ALGM DIOD POWI AOSL NVTS WOLF INDI VICR",
    "Semis: Mobile & RF": "QCOM SWKS QRVO CRUS HIMX CEVA PI",
    "Semis: IoT, Edge & FPGA": "LSCC SITM SLAB SYNA AMBQ NVEC LAES",
    "Semi Equipment: Front-End": "ASML AMAT LRCX KLAC NVMI ONTO CAMT ACMR ACLS VECO",
    "Semi Equipment: Test & Packaging": "TER FORM COHU AEHR KLIC AMKR ASX IMOS",
    "Semi Materials & Subsystems": "ENTG Q AXTI PLAB UCTT ICHR NANO MKSI",
    "Optical Networking & Photonics": "COHR LITE AAOI FN CIEN POET LPTH LASR VIAV",
    "AI Servers": "DELL SMCI HPE PENG",
    "Contract Electronics Manufacturing": "CLS FLEX JBL SANM PLXS BHE TTMI",
    "Networking Equipment": "ANET CSCO UI EXTR NTGR ADTN CLFD CALX HLIT DGII NOK ERIC",
    "Storage Systems": "NTAP P QMCO",
    "PCs, Devices & Peripherals": "AAPL HPQ LOGI CRSR CRCT SONY SONO LPL",
    "3D Printing": "SSYS DDD",
    "Satellite Communications": "ASTS VSAT TSAT GILT IRDM",
    "Connectors & Passive Components": "APH TEL GLW LFUS VSH BELFB BELFA ROG CTS KN MEI ALNT",
    "Test, Measurement & Sensors": "KEYS TDY CGNX NOVT ST VPG ESE",
    "IT Consulting & Outsourcing": "ACN INFY CTSH WIT GIB EPAM G EXLS GLOB GDYN DXC KD CNXC TASK IBEX HCKT III FORTY CINT",
    "Government IT & Defense Services": "LDOS CACI SAIC PSN BAH",
    "Financial Tech Processors": "FIS JKHY BR FISV GPN",
    "China Data Centers": "GDS VNET",
    "Digital Ads & Social Media": "GOOGL GOOG META PINS SNAP RDDT TBLA NXDR",
    "China Internet": "BIDU TME BILI JOYY WB MOMO ATHM BZ",
    "Online Marketplaces & Listings": "ZG Z CARG CARS YELP UPWK FVRR ZIP GRPN EVER MAX NRDS",
}
EXCLUDE = {"Preferred & Duplicate Shares"}        # not ranked (a second share class of a company already counted)
HAND = {s: g for g, syms in G.items() for s in syms.split()}
# Banks - Regional not listed above: mid-size ($3B+) vs community
REGIONAL_MID = 3.0


def group_of(sym, prof, stock):
    if sym in HAND:
        return HAND[sym]
    ind = prof.get("industry") or stock.get("industry") or "Other"
    if ind in ("Banks - Regional", "Banks - Diversified"):
        return "Banks: US Regional" if (stock.get("mcap_b") or 0) >= REGIONAL_MID else "Banks: US Community"
    if ind == "Biotechnology":
        return "Biotech: Other"
    if ind.startswith("Software"):
        return "Software: Other"
    return ind


def main():
    P = json.load(open(sys.argv[1]))["rows"]
    S = {r["symbol"]: r for r in json.load(open(sys.argv[2]))}
    out = {s: group_of(s, P.get(s, {}), S[s]) for s in S}
    json.dump(out, open(sys.argv[3], "w"), indent=0, sort_keys=True)
    print(json.dumps({"stocks": len(out), "groups": len(set(out.values())), "hand": sum(1 for s in S if s in HAND)}))


if __name__ == "__main__":
    main()

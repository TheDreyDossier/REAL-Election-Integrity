# The REAL Election Integrity

**A fact-checked counter to the U.S. Department of Justice's "Election Integrity" dashboard, launched July 16, 2026 at [civilrights.justice.gov/electionintegrity](https://civilrights.justice.gov/electionintegrity).**

---

## The single sentence

The DOJ dashboard displays 51 completed enforcement actions dated **September 18, 2026** — a date that is nine weeks in the future.

That is not a typo. It is the structural design of the site.

## The arithmetic

| | Count | Share |
|---|---:|---:|
| Total "verified enforcement actions" displayed | **243** | 100% |
| Duplicates of just 4 templates | **156** | 64% |
| Underlying real items behind those templates | **4** | — |
| Entries with any source link on the DOJ site | **32** | 13.2% |
| Entries dated in the future as of launch (July 16, 2026) | **72** | 30% |
| Entries attributed to DHS (the co-branded agency) | **0** | 0% |

## The four templates

Of the 243 entries, 156 (64%) are duplicates of just four underlying items:

1. **"Warns State Officials of Criminal Liability"** — 51 entries. One letter, identical text, sent to all 51 chief election officials on July 7, 2026. Some delivered via generic public email inboxes.
2. **"Ensures Primary Election Military Ballots"** — 51 entries. The routine UOCAVA compliance program DOJ has run every federal election cycle since 1986.
3. **"Ensures General Election Military Ballots"** — 51 entries, all dated 9/18/2026. Future-dated on the day of launch. Presented as accomplished.
4. **"Withdrew from Biden-Era Race-Based Election Maps"** — 3 entries. Actually 7 Voting Rights Act withdrawals; the Alabama entry links to a voter-roll purge case, not a redistricting case.

Full analysis: [`analysis/STRUCTURAL_EXPOSE.md`](analysis/STRUCTURAL_EXPOSE.md)

## Repository layout

```
REAL-Election-Integrity/
├── README.md                              ← you are here
├── analysis/
│   └── STRUCTURAL_EXPOSE.md               ← the one-page structural argument
├── evidence/
│   ├── captured/                          ← DOJ site as-of 2026-07-16, verbatim
│   │   ├── page.html                      ← the launched dashboard
│   │   ├── headers.txt                    ← response headers (proves infra stack)
│   │   ├── election-integrity-map-data.json  ← the full 243-entry dataset
│   │   ├── agency-badge-map.json
│   │   ├── map-widget-d3geo.js
│   │   ├── page_text.txt                  ← cleaned main-page text
│   │   ├── state_urls.txt                 ← 51 state detail-page URLs
│   │   └── state_pages/                   ← all 51 detail pages, verbatim
│   ├── data/
│   │   ├── CLAIM_INVENTORY.md             ← every claim, organized by template + state
│   │   ├── all_claims_master.csv          ← flat 243-row CSV
│   │   ├── election_integrity_actions.csv ← alternate 243-row layout
│   │   └── individual_claims.txt          ← 87 unique individual claim strings
│   └── verifications/                     ← per-template verification memos
│       ├── T1_criminal_liability_letter.md
│       ├── T2_T3_uocava_military_ballots.md
│       └── T4_biden_era_race_maps_withdrawal.md
├── site/                                  ← the counter-site (in progress)
├── monitoring/                            ← scripts to re-fetch DOJ site over time
└── .github/workflows/                     ← optional daily re-fetch + diff
```

## Method

**Lawful OSINT only.** No authentication bypassed. No PII collected. No private systems accessed. No fake submissions.

**Confidence labels** used throughout:

- **CONFIRMED** — multiple primary sources agree
- **PROBABLE** — single strong primary source
- **UNVERIFIED** — unable to substantiate
- **CONTRADICTED** — primary source disagrees with the DOJ dashboard

The four templates covered in this initial release are all **CONFIRMED**.

## Site fingerprint (for the record)

- URL: `civilrights.justice.gov/electionintegrity`
- Deployed: 2026-07-16 22:01:54 UTC (3:01 PM PDT, July 16, 2026)
- Hosting: cloud.gov / Cloud Foundry, AWS GovCloud us-gov-west-1, CloudFront edge
- Front-end: U.S. Web Design System (USWDS), D3.js choropleth, jQuery
- Analytics: DAP + Google Tag Manager + GA4 (`UA-176942176-1`, `G-2T865GKYYK`)
- Report intake CTAs route to the existing DOJ Civil Rights complaint form and the DHS homepage; no dedicated election-integrity intake exists

## Status

- [x] DOJ site captured verbatim (page, data, 51 state pages, headers, JS)
- [x] Claim inventory: all 243 entries catalogued
- [x] Tier 1 verifications complete (4 templates → 156 of 243 rows resolved)
- [x] Structural exposé drafted
- [ ] Tier 2: 12 sourced individual lawsuits (CourtListener docket checks)
- [ ] Tier 3: 5 DHS press releases
- [ ] Tier 4: DOJ election monitor deployments (AZ, MA, MI, MN, NH, NJ, VA)
- [ ] Tier 5: Remaining ~55 unsourced individual claims
- [ ] Counter-site build (mirror USWDS + D3 layout, per-state refutations)
- [ ] Monitoring cron for DOJ-site changes over time

## License

All rights reserved. This is an active research and journalism project. Do not redistribute or re-publish without permission. Citing individual facts with attribution is fine and encouraged for reporters and oversight staff.

## Contact

Via [The Drey Dossier](https://github.com/TheDreyDossier).

#!/usr/bin/env python3
"""
Site generator for The REAL Election Integrity.
Consumes evidence/captured/election-integrity-map-data.json
and evidence/verifications/*.md, produces static HTML.
"""

import json
import os
from datetime import date
from pathlib import Path

# ==========================================================
# Paths
# ==========================================================
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
DATA_PATH = REPO / "evidence" / "captured" / "election-integrity-map-data.json"
OUT = ROOT
STATE_OUT = OUT / "states"
STATE_OUT.mkdir(exist_ok=True)

# ==========================================================
# Load data
# ==========================================================
with open(DATA_PATH) as f:
    STATES = json.load(f)

# STATES is a dict keyed by 2-letter code with {name, url, actions[]}
# Compute totals
TOTAL_ACTIONS = sum(len(s["actions"]) for s in STATES.values())
STATE_COUNT = len(STATES)  # 51

# Parse action dates and determine which are in the future
TODAY = date(2026, 7, 16)

def parse_date(s):
    """DOJ uses M/D/YYYY."""
    try:
        m, d, y = s.split("/")
        return date(int(y), int(m), int(d))
    except Exception:
        return None

# ==========================================================
# Classify each action into a template + verdict
# ==========================================================
TEMPLATE_MAP = {
    "criminal_liability": {
        "matcher": lambda a: "Criminal Liability" in a["action"] and "Illegal Voting" in a["action"],
        "verdict": "Count inflation",
        "verdict_class": "misleading",
        "body": (
            "This is <strong>one letter</strong>, signed by Assistant Attorney General Harmeet Dhillon on July 7, 2026 and sent "
            "the same day to all 51 chief state election officials with identical language. "
            "It is being counted as 51 separate enforcement actions on this dashboard. "
            "<a href='https://www.votebeat.org/national/2026/07/07/trump-department-justice-letter-noncitizens-voter-rolls-election-officials/'>Votebeat</a> "
            "found the letter was delivered to some states through generic public inboxes, "
            "not tailored investigations."
        ),
        "sources": [
            ("Reuters", "https://www.reuters.com/legal/government/us-justice-department-tells-state-officials-they-could-be-prosecuted-over-2026-07-08/"),
            ("Votebeat", "https://www.votebeat.org/national/2026/07/07/trump-department-justice-letter-noncitizens-voter-rolls-election-officials/"),
            ("ABC News", "https://abcnews.com/US/ahead-midterms-doj-warns-state-officials-potential-criminal/story?id=134566080"),
            ("NOTUS", "https://www.notus.org/2026-election/doj-threat-election-officials"),
        ],
        "memo": "T1_criminal_liability_letter.md",
    },
    "primary_uocava": {
        "matcher": lambda a: "Primary Election Military Ballots" in a["action"],
        "verdict": "Routine work reframed",
        "verdict_class": "misleading",
        "body": (
            "This is <strong>routine annual UOCAVA compliance monitoring</strong>, a program the DOJ Civil Rights Division has run every federal "
            "election cycle since 1986 in every state under the Uniformed and Overseas Citizens Absentee Voting Act. "
            "In DOJ's own March 2026 letter to California: <em>&#8220;Pursuant to our UOCAVA enforcement authority, we will request, "
            "as we have in prior election cycles, that your office monitor the transmission of absentee ballots.&#8221;</em> "
            "The Biden DOJ ran the same program for the 2024 cycle."
        ),
        "sources": [
            ("DOJ CRT — UOCAVA overview", "https://www.justice.gov/crt/uniformed-and-overseas-citizens-absentee-voting-act"),
            ("DOJ 2010 UOCAVA report to Congress", "https://www.justice.gov/sites/default/files/crt/legacy/2011/01/13/move_act_report.pdf"),
            ("Democracy Docket — Trump DOJ 2026 letter", "https://www.democracydocket.com/news-alerts/trump-doj-expands-crackdown-on-overseas-voters-over-id/"),
            ("Biden DOJ 2024 UOCAVA agreements", "https://www.justice.gov/archives/opa/pr/justice-department-reached-agreements-protect-rights-military-and-overseas-voters-new-york"),
        ],
        "memo": "T2_T3_uocava_military_ballots.md",
    },
    "general_uocava": {
        "matcher": lambda a: "General Election Military Ballots" in a["action"],
        "verdict": "Future-dated as accomplished",
        "verdict_class": "misleading",
        "body": (
            "This entry is dated <strong>September 18, 2026</strong> &mdash; the statutory 45-day deadline under 52 U.S.C. &sect; 20302(a)(8)(A) "
            "by which states must mail absentee ballots to military and overseas voters. That date is <strong>after</strong> the DOJ "
            "dashboard launched. The event has not yet occurred, but is displayed today as a completed, verified federal enforcement action. "
            "Compliance is a state obligation; DOJ's role is monitoring."
        ),
        "sources": [
            ("52 U.S.C. § 20302 (UOCAVA)", "https://www.law.cornell.edu/uscode/text/52/20302"),
            ("DOJ CRT — UOCAVA overview", "https://www.justice.gov/crt/uniformed-and-overseas-citizens-absentee-voting-act"),
            ("Federal Voting Assistance Program", "https://www.fvap.gov/info/laws/uocava"),
        ],
        "memo": "T2_T3_uocava_military_ballots.md",
    },
    "race_maps": {
        "matcher": lambda a: "Race-Based Election Maps" in a["action"] and "Withdrew" in a["action"],
        "verdict": "Mischaracterized",
        "verdict_class": "misleading",
        "body": (
            "DOJ has withdrawn from <strong>seven</strong> Voting Rights Act Section 2 cases according to the "
            "<a href='https://www.brennancenter.org/our-work/analysis-opinion/justice-department-shirking-its-responsibility-voters'>Brennan Center</a>, "
            "not three. In <em>Louisiana v. Callais</em>, DOJ did not merely withdraw &mdash; it filed a new brief on 9/25/2025 arguing "
            "Section 2 of the Voting Rights Act is unconstitutional. In Alabama, DOJ's own linked press release describes a "
            "<a href='https://www.justice.gov/opa/pr/us-department-justice-dismisses-biden-era-lawsuit-against-alabama-order-have-more-secure'>voter-roll purge case</a>, "
            "not a race-based redistricting case."
        ),
        "sources": [
            ("Brennan Center — 7 VRA case withdrawals", "https://www.brennancenter.org/our-work/analysis-opinion/justice-department-shirking-its-responsibility-voters"),
            ("Democracy Docket — Callais brief", "https://www.democracydocket.com/news-alerts/once-the-voting-rights-acts-champion-doj-now-wants-scotus-to-gut-it/"),
            ("Texas Tribune — TX withdrawal", "https://www.texastribune.org/2025/03/13/texas-redistricting-lawsuit-justice-department-withdraws/"),
            ("Wikipedia — Louisiana v. Callais", "https://en.wikipedia.org/wiki/Louisiana_v._Callais"),
        ],
        "memo": "T4_biden_era_race_maps_withdrawal.md",
    },
}

def classify(action):
    for key, t in TEMPLATE_MAP.items():
        if t["matcher"](action):
            return key, t
    return None, None

# Precompute counts per template
TEMPLATE_COUNTS = {k: 0 for k in TEMPLATE_MAP}
FUTURE_COUNT = 0
SOURCED_COUNT = 0  # can't compute from JSON alone; use known 32
for state_code, state in STATES.items():
    for a in state["actions"]:
        key, _ = classify(a)
        if key:
            TEMPLATE_COUNTS[key] += 1
        d = parse_date(a["date"])
        if d and d > TODAY:
            FUTURE_COUNT += 1

TEMPLATED_TOTAL = sum(TEMPLATE_COUNTS.values())
UNDERLYING_REAL = 4  # T1 (1 letter) + T2 (1 program) + T3 (1 program) + T4 (7 cases displayed as 3)

# ==========================================================
# HTML fragments
# ==========================================================

def head(title, description, canonical="/"):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://realelectionintegrity.com{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Public+Sans:wght@400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">
<link rel="stylesheet" href="/css/style.css?v=putin-hero-1">
<title>{title}</title>
</head>
<body>
'''

HEADER = '''<header class="site-header">
  <div class="container">
    <a class="site-brand" href="/">
      <img class="logo" src="/assets/logo.svg" alt="The Drey Dossier seal">
      <span class="brand-text">
        <span class="kicker">The Drey Dossier</span>
        <span class="primary">REAL Election Integrity Division</span>
      </span>
    </a>
    <nav class="site-nav" aria-label="Primary">
      <a href="/">Home</a>
      <a href="/about.html">About</a>
      <a href="/method.html">Method</a>
      <a href="/#states">States</a>
      <a href="/report-an-error.html">Report an Error</a>
    </nav>
  </div>
</header>

<div class="tagline-banner">
  <div class="container">
    Get involved and learn more about the division's <a href="https://civilrights.justice.gov/electionintegrity" rel="external nofollow">election-integrity enforcement actions.</a>
  </div>
</div>
'''

FOOTER = '''<footer class="site-footer">
  <div class="container">
    <div class="about">
      <h4>About this site</h4>
      <p>The REAL Election Integrity is an independent fact-check of the U.S. Department of Justice's <a href="https://civilrights.justice.gov/electionintegrity">Election Integrity dashboard</a>, launched July 16, 2026. This site is <strong>not</strong> a government website and is not affiliated with the Department of Justice, the Department of Homeland Security, or any federal agency.</p>
      <p>Every claim on the DOJ dashboard has been catalogued and, where possible, verified against primary sources. All evidence is public at <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity">github.com/TheDreyDossier/REAL-Election-Integrity</a>.</p>
    </div>
    <div class="link-column">
      <h4>Analysis</h4>
      <a href="/#reduction">The 243 &rarr; 4 reduction</a>
      <a href="/about.html">The structural exposé</a>
      <a href="/method.html">Method &amp; confidence labels</a>
    </div>
    <div class="link-column">
      <h4>Evidence</h4>
      <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity">GitHub repository</a>
      <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity/tree/main/evidence/verifications">Verification memos</a>
      <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity/tree/main/evidence/captured">Site capture</a>
    </div>
    <div class="disclaimer">
      This site is a work of independent journalism and civic accountability. It reproduces DOJ visual language for the purpose of side-by-side comparison and fact-checking. No content on this site is issued by, endorsed by, or affiliated with any federal agency. All trademarks, seals, and imagery of the U.S. government remain the property of the U.S. government. All rights reserved © 2026 The Drey Dossier.
    </div>
  </div>
</footer>
</body>
</html>
'''

def state_slug(code):
    return STATES[code]["name"].lower().replace(" ", "-")

# ==========================================================
# HOMEPAGE
# ==========================================================
def render_home():
    # State grid with counts
    state_cards = []
    for code in sorted(STATES.keys(), key=lambda c: STATES[c]["name"]):
        s = STATES[code]
        n = len(s["actions"])
        state_cards.append(
            f'<a href="/states/{state_slug(code)}.html"><span>{s["name"]}</span><span class="count">{n}</span></a>'
        )
    state_grid_html = "\n      ".join(state_cards)

    html = head(
        "The REAL Election Integrity — Fact-checking DOJ's Election Integrity dashboard",
        "An independent fact-check of the U.S. Department of Justice's Election Integrity dashboard, launched July 16, 2026. 243 claimed enforcement actions reduce to 4 real items.",
        canonical="/",
    )
    html += HEADER
    html += f'''
<section class="hero hero-image">
  <div class="hero-bg" role="presentation" aria-hidden="true"></div>
  <div class="hero-scrim" aria-hidden="true"></div>
  <div class="container hero-content">
    <h1 class="hero-title">REAL Enforcement Actions to<br>Safeguard Election Integrity</h1>
    <p class="hero-sub">from the DOJ&rsquo;s lies</p>
    <p class="lede">The U.S. Department of Justice launched a public &ldquo;Election Integrity&rdquo; dashboard claiming <strong>243 enforcement actions</strong>. Fifty-one are dated <strong>September 18, 2026</strong> — nine weeks in the future. This site is a line-by-line fact-check.</p>
    <div class="meta">
      <span><strong>{TOTAL_ACTIONS}</strong> total &ldquo;verified enforcement actions&rdquo;</span>
      <span><strong>{TEMPLATED_TOTAL} of {TOTAL_ACTIONS}</strong> are duplicates of {UNDERLYING_REAL} templates</span>
      <span><strong>{FUTURE_COUNT}</strong> dated in the future as of launch</span>
      <span><strong>13.2%</strong> have any source link on the DOJ site</span>
    </div>
    <p class="hero-caption">Trump &amp; Putin, Joint Base Elmendorf-Richardson, Anchorage, Alaska, <a href="https://www.theguardian.com/us-news/2026/jan/29/trump-putin-white-house-photo">August 15, 2025</a>. Trump kept this photo framed in the Palm Room of the White House. When critics objected, he removed the photo of his granddaughter beneath it — not the photo of Putin.</p>
  </div>
</section>

<section class="hero-quote">
  <div class="container">
    <blockquote>
      <p>&ldquo;They have information &mdash; I think I&rsquo;d take it&hellip; It&rsquo;s not an interference, they have information, I think I&rsquo;d take it.&rdquo;</p>
      <cite>President Donald J. Trump, ABC News interview with George Stephanopoulos, <a href="https://www.bbc.co.uk/news/world-us-canada-48618273">June 12, 2019</a> — on whether he would accept opposition research on a political opponent from a foreign government.</cite>
    </blockquote>
  </div>
</section>

<section id="reduction">
  <div class="container">
    <div class="section-header">
      <div class="kicker">The Arithmetic</div>
      <h2>243 &rarr; 4</h2>
    </div>
    <p style="max-width:800px;font-size:1.0625rem;">Of the 243 &ldquo;verified enforcement actions&rdquo; on the DOJ dashboard, <strong>{TEMPLATED_TOTAL} ({int(100*TEMPLATED_TOTAL/TOTAL_ACTIONS)}%)</strong> are duplicates of just four underlying items, each replicated once per state. Consolidating those templates to their real items, the map's {TOTAL_ACTIONS} entries reduce to approximately <strong>90 discrete claims</strong> &mdash; of which only 32 (13.2%) carry any source link.</p>

    <table class="reduction-table">
      <thead>
        <tr>
          <th>What DOJ calls it</th>
          <th style="text-align:center;">Rows on dashboard</th>
          <th>What it actually is</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>&ldquo;Warns State Officials of Criminal Liability&rdquo;</strong><br><span class="text-mono">dated 7/7/2026</span></td>
          <td class="count">{TEMPLATE_COUNTS['criminal_liability']}</td>
          <td>One letter, identical text, signed by Asst. AG Harmeet Dhillon, sent to all 51 chief election officials on the same day. Some delivered via generic public email inboxes. <a href="/analysis.html#t1">Fact-check &rarr;</a></td>
        </tr>
        <tr>
          <td><strong>&ldquo;Ensures Primary Election Military Ballots&rdquo;</strong><br><span class="text-mono">various 2026 dates</span></td>
          <td class="count">{TEMPLATE_COUNTS['primary_uocava']}</td>
          <td>The routine UOCAVA compliance-monitoring program DOJ has run every federal election cycle since 1986, in every state. Not enforcement &mdash; monitoring. <a href="/analysis.html#t2">Fact-check &rarr;</a></td>
        </tr>
        <tr>
          <td><strong>&ldquo;Ensures General Election Military Ballots&rdquo;</strong><br><span class="text-mono">dated 9/18/2026</span></td>
          <td class="count">{TEMPLATE_COUNTS['general_uocava']}</td>
          <td>Same routine program &mdash; but dated 64 days <em>after</em> the dashboard launched. The statutory 45-day ballot-mailing deadline itself, presented as accomplished enforcement. <a href="/analysis.html#t3">Fact-check &rarr;</a></td>
        </tr>
        <tr>
          <td><strong>&ldquo;Withdrew from Biden-Era Race-Based Election Maps&rdquo;</strong></td>
          <td class="count">{TEMPLATE_COUNTS['race_maps']}</td>
          <td>Actually seven VRA Section 2 case withdrawals, not three. Alabama entry links to a voter-roll purge case, not a redistricting case. <a href="/analysis.html#t4">Fact-check &rarr;</a></td>
        </tr>
        <tr class="total">
          <td><strong>Total</strong></td>
          <td class="count">{TEMPLATED_TOTAL}</td>
          <td><strong>of {TOTAL_ACTIONS} entries · resolve to <span style="color:#8b0a03;">4 real items</span></strong></td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-header">
      <div class="kicker">By the Numbers</div>
      <h2>The scale problem</h2>
    </div>
    <div class="big-stats">
      <div class="big-stat">
        <div class="number">{TOTAL_ACTIONS}</div>
        <div class="label">Total &ldquo;enforcement actions&rdquo; displayed</div>
        <div class="sublabel">Across all 50 states plus D.C.</div>
      </div>
      <div class="big-stat">
        <div class="number">4</div>
        <div class="label">Underlying real items</div>
        <div class="sublabel">After collapsing the 4 duplicated templates</div>
      </div>
      <div class="big-stat">
        <div class="number">{FUTURE_COUNT}</div>
        <div class="label">Dated in the future as of launch</div>
        <div class="sublabel">Presented today as accomplished</div>
      </div>
      <div class="big-stat">
        <div class="number">13.2%</div>
        <div class="label">Have any source link at all</div>
        <div class="sublabel">32 of 243 entries link to a source</div>
      </div>
      <div class="big-stat">
        <div class="number">0</div>
        <div class="label">Entries attributed to DHS</div>
        <div class="sublabel">Despite the site being co-branded with DHS</div>
      </div>
      <div class="big-stat">
        <div class="number">51</div>
        <div class="label">States displayed as separately &ldquo;warned&rdquo;</div>
        <div class="sublabel">One mass letter, counted 51 times</div>
      </div>
    </div>
  </div>
</section>

<section id="states">
  <div class="container">
    <div class="section-header">
      <div class="kicker">State by State</div>
      <h2>Every state on the dashboard, fact-checked</h2>
    </div>
    <p style="max-width:800px;">Each state page lists the DOJ dashboard's entries verbatim, with an inline fact-check on every action that has been verified. Number next to each state = entries on DOJ's dashboard.</p>
    <div class="state-grid">
      {state_grid_html}
    </div>
  </div>
</section>

<section class="section-dark">
  <div class="container container-narrow">
    <h2 style="color:white;margin-top:0;">Why this matters</h2>
    <p style="font-size:1.125rem;line-height:1.55;color:rgba(255,255,255,0.9);">A public-facing federal enforcement dashboard, distributed under the U.S. Department of Justice's civil rights domain, is the highest-credibility surface the executive branch has for representing what its law enforcement is doing.</p>
    <p style="font-size:1.125rem;line-height:1.55;color:rgba(255,255,255,0.9);">When that surface displays future events as accomplished, routine statutory work as discretionary wins, one letter as 51 investigations, and reframes Voting Rights Act retreat as courtroom victory, it converts an oversight instrument into a campaign instrument.</p>
    <p style="font-size:1.125rem;line-height:1.55;color:rgba(255,255,255,0.9);">The distinction matters because voters, reporters, election administrators, and courts rely on federal enforcement reporting to distinguish real activity from claimed activity ahead of a midterm.</p>
    <p style="font-size:1.125rem;line-height:1.55;color:rgba(255,255,255,0.9);"><strong>The four items are the story. The 243 count is the frame.</strong></p>
  </div>
</section>
'''
    html += FOOTER
    return html

# ==========================================================
# STATE PAGE
# ==========================================================
def render_state(code):
    state = STATES[code]
    name = state["name"]
    doj_url = state["url"]

    action_items = []
    for a in state["actions"]:
        d = parse_date(a["date"])
        is_future = bool(d and d > TODAY)
        future_class = " future" if is_future else ""
        future_note = " <span style='color:#936f38;font-weight:600;font-size:0.8125rem;'>(FUTURE-DATED)</span>" if is_future else ""

        key, tmpl = classify(a)
        fc_html = ""
        if tmpl:
            sources_html = " · ".join(f'<a href="{u}">{n}</a>' for n, u in tmpl["sources"])
            fc_html = f'''<div class="fact-check">
        <div class="fc-header">
          <span class="fc-badge">Fact Check</span>
          <span class="fc-verdict">{tmpl["verdict"]}</span>
        </div>
        <div class="fc-body">{tmpl["body"]}</div>
        <div class="fc-sources"><strong>Sources:</strong> {sources_html} · <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity/blob/main/evidence/verifications/{tmpl["memo"]}">Full memo &rarr;</a></div>
      </div>'''
        else:
            fc_html = f'''<div class="fact-check unverified">
        <div class="fc-header">
          <span class="fc-badge">Fact Check</span>
          <span class="fc-verdict">Unverified &mdash; pending Tier 2 review</span>
        </div>
        <div class="fc-body">This individual claim is not part of the four structural templates. It is being reviewed against primary sources (docket filings, press releases, state responses). Status will be updated here as verification completes.</div>
      </div>'''

        action_items.append(f'''<li class="action-item">
      <div class="action-header">
        <span class="date-badge{future_class}">{a["date"]}{future_note}</span>
        <span class="agency-badge">{a["agency"]}</span>
      </div>
      <div class="claim-title">{a["action"]}</div>
      {fc_html}
    </li>''')

    actions_html = "\n    ".join(action_items)

    html = head(
        f"{name} — Fact-check of DOJ's Election Integrity dashboard | The REAL Election Integrity",
        f"Every DOJ-dashboard claim for {name}, catalogued and fact-checked against primary sources.",
        canonical=f"/states/{state_slug(code)}.html",
    )
    html += HEADER
    html += f'''
<div class="container">
  <div class="breadcrumbs">
    <a href="/">Home</a>
    <span class="sep">&rsaquo;</span>
    <a href="/#states">States</a>
    <span class="sep">&rsaquo;</span>
    <span>{name}</span>
  </div>
</div>

<section style="padding-top: 24px; padding-bottom: 24px;">
  <div class="container">
    <div class="section-header">
      <div class="kicker">State fact-check · {name}</div>
      <h2 style="margin-top:0;">{name}</h2>
    </div>
    <p style="max-width:800px;font-size:1.0625rem;">DOJ's dashboard lists <strong>{len(state["actions"])} enforcement actions</strong> for {name}. Below is every entry verbatim, with an inline fact-check on each claim that falls into the four structural templates. DOJ's own page for {name}: <a href="{doj_url}" rel="external nofollow">{doj_url}</a>.</p>

    <ol class="action-list">
    {actions_html}
    </ol>

    <div class="callout">
      <h3 style="margin-top:0;">About the fact-checks on this page</h3>
      <p style="margin-bottom:0;">Fact-checks in red are for claims that fall into one of the four structural templates identified in <a href="/#reduction">our arithmetic analysis</a>. Fact-checks in yellow are individual, per-state claims currently pending Tier 2 verification against docket records and press releases. Everything is public and versioned at <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity">github.com/TheDreyDossier/REAL-Election-Integrity</a>.</p>
    </div>
  </div>
</section>
'''
    html += FOOTER
    return html

# ==========================================================
# ABOUT / ANALYSIS PAGE — pulls STRUCTURAL_EXPOSE.md
# ==========================================================
def render_about():
    # Read the structural expose markdown and roughly convert to HTML sections
    html = head(
        "About & Analysis — The REAL Election Integrity",
        "The full structural exposé of the DOJ Election Integrity dashboard: 243 claimed enforcement actions reduce to 4 real items.",
        canonical="/about.html",
    )
    html += HEADER
    html += '''
<div class="container">
  <div class="breadcrumbs">
    <a href="/">Home</a> <span class="sep">&rsaquo;</span> <span>About</span>
  </div>
</div>

<section style="padding-top: 24px;">
  <div class="container container-narrow">
    <div class="section-header">
      <div class="kicker">Structural Exposé</div>
      <h2 style="margin-top:0;">How 4 items became 243</h2>
    </div>

    <p style="font-size:1.125rem;line-height:1.55;"><strong>The DOJ's new Election Integrity dashboard displays 51 completed enforcement actions dated September 18, 2026 — a date that is nine weeks in the future.</strong></p>
    <p>That is not a typo. It is the structural design of the site.</p>

    <h3 id="what-shown">What the dashboard shows</h3>
    <p>Launched July 16, 2026 at <a href="https://civilrights.justice.gov/electionintegrity">civilrights.justice.gov/electionintegrity</a>, the site presents itself as a real-time map of federal election-integrity enforcement:</p>
    <ul style="margin-left: 1.5rem; margin-bottom: 1.5rem;">
      <li>243 &ldquo;verified enforcement actions&rdquo;</li>
      <li>Across all 50 states plus D.C.</li>
      <li>All attributed to the Department of Justice</li>
      <li>Each state's page shows dated, individually-numbered actions</li>
    </ul>
    <p>The visual language &mdash; a D3 choropleth map, per-state dossiers, action counts, a &ldquo;Report a Violation&rdquo; button &mdash; is designed to convey scale, momentum, and rigor.</p>

    <h3>What is actually there</h3>
    <p>Of the 243 entries, <strong>156 (64%)</strong> are duplicates of just <strong>four</strong> underlying items, each replicated once per state. See the <a href="/#reduction">reduction table</a> for the full breakdown.</p>

    <h2>The four structural problems</h2>

    <h3 id="t3">1. Future-dated enforcement</h3>
    <p>Fifty-one entries are dated <strong>September 18, 2026</strong> &mdash; the statutory deadline under 52 U.S.C. § 20302(a)(8)(A) by which states must mail absentee ballots to military and overseas voters (exactly 45 days before Election Day). It is a deadline states are required by law to meet. It has not yet arrived.</p>
    <p>The dashboard displays these entries today, July 16, 2026, as <strong>verified, completed federal enforcement actions</strong>.</p>
    <p>This is the single cleanest structural fact: an event that has not happened is presented as an event that has been accomplished.</p>

    <h3 id="t2">2. Category error: routine compliance as enforcement</h3>
    <p>The Uniformed and Overseas Citizens Absentee Voting Act of 1986 (UOCAVA), amended by the MOVE Act of 2009, requires DOJ's Civil Rights Division Voting Section to monitor UOCAVA compliance in every state, in every federal election cycle. DOJ's own annual reports to Congress &mdash; <a href="https://www.justice.gov/sites/default/files/crt/legacy/2011/01/13/move_act_report.pdf">2010</a>, <a href="https://www.justice.gov/sites/default/files/crt/legacy/2014/01/09/2013_uocava_report.pdf">2013</a>, and every year since &mdash; document the same pattern.</p>
    <p>In DOJ's own <a href="https://www.democracydocket.com/wp-content/uploads/2026/03/CA-DOJ-UOCAVA-1.pdf">March 2026 letter to California</a>:</p>
    <blockquote style="border-left:4px solid var(--color-primary); padding-left: 1rem; color: var(--color-base-dark); font-style: italic; margin: 1rem 0;">Pursuant to our UOCAVA enforcement authority, we will request, <strong>as we have in prior election cycles</strong>, that your office monitor the transmission of absentee ballots...</blockquote>
    <p>Routine, statutorily-mandated, bipartisan-continuity compliance work is being displayed as 102 discrete Trump-era enforcement wins.</p>

    <h3 id="t1">3. Count inflation: one letter as 51 actions</h3>
    <p>On July 7, 2026, DOJ sent an identical letter to the chief election officials of all 50 states plus D.C., warning of potential criminal liability for allowing noncitizens to remain on voter rolls. The story was covered the same day by <a href="https://www.reuters.com/legal/government/us-justice-department-tells-state-officials-they-could-be-prosecuted-over-2026-07-08/">Reuters</a>, <a href="https://www.votebeat.org/national/2026/07/07/trump-department-justice-letter-noncitizens-voter-rolls-election-officials/">Votebeat</a>, <a href="https://abcnews.com/US/ahead-midterms-doj-warns-state-officials-potential-criminal/story?id=134566080">ABC News</a>, and others.</p>
    <p>Votebeat's reporting found the letter was delivered to some states through <em>generic public-facing email inboxes</em> &mdash; the kind used to route citizen inquiries. It was a mass communication, not 51 individually-tailored investigations. The dashboard converts one letter into 51 numbered &ldquo;enforcement actions.&rdquo;</p>

    <h3 id="t4">4. Mischaracterization: &ldquo;withdrew from Biden-era race maps&rdquo;</h3>
    <p>Three states &mdash; Alabama, Louisiana, and Texas &mdash; carry entries claiming DOJ &ldquo;Withdrew from Biden-Era Suit Demanding Race-Based Election Maps.&rdquo; This is misleading in three ways:</p>
    <ul style="margin-left:1.5rem;margin-bottom:1.5rem;">
      <li><strong>The Alabama entry links to the wrong case.</strong> DOJ's own <a href="https://www.justice.gov/opa/pr/us-department-justice-dismisses-biden-era-lawsuit-against-alabama-order-have-more-secure">press release</a> &mdash; linked directly from the dashboard &mdash; describes dismissal of a voter roll purge case, not a race-based redistricting case.</li>
      <li><strong>There are seven, not three.</strong> According to the <a href="https://www.brennancenter.org/our-work/analysis-opinion/justice-department-shirking-its-responsibility-voters">Brennan Center</a>, DOJ has withdrawn from seven Section 2 Voting Rights Act cases. The other four are omitted from the dashboard.</li>
      <li><strong>&ldquo;Biden-era&rdquo; obscures the legal context.</strong> In Louisiana v. Callais, <a href="https://www.democracydocket.com/news-alerts/once-the-voting-rights-acts-champion-doj-now-wants-scotus-to-gut-it/">Democracy Docket reports</a> DOJ filed a new brief on September 25, 2025 arguing Section 2 is unconstitutional. In dissent, Justice Kagan wrote that the majority &ldquo;renders Section 2 all but a dead letter.&rdquo;</li>
    </ul>

    <h3>Site fingerprint (for the record)</h3>
    <ul style="margin-left:1.5rem;">
      <li>URL: <span class="text-mono">civilrights.justice.gov/electionintegrity</span></li>
      <li>Deployed: 2026-07-16 22:01:54 UTC (3:01 PM PDT, July 16, 2026)</li>
      <li>Hosting: cloud.gov / Cloud Foundry, AWS GovCloud us-gov-west-1, CloudFront edge</li>
      <li>Front-end: U.S. Web Design System (USWDS), D3.js choropleth, jQuery</li>
      <li>Analytics: DAP + Google Tag Manager + GA4</li>
      <li>Report intake CTAs route to the existing DOJ Civil Rights complaint form and the DHS homepage; no dedicated election-integrity intake exists</li>
    </ul>

    <div class="callout">
      <p style="margin-bottom:0;"><strong>Method note.</strong> Every claim above is verifiable against the dashboard's own data and primary sources. Per-template verification memos with full source lists are archived at <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity/tree/main/evidence/verifications">github.com/TheDreyDossier/REAL-Election-Integrity/evidence/verifications</a>.</p>
    </div>
  </div>
</section>
'''
    html += FOOTER
    return html

# ==========================================================
# METHOD PAGE
# ==========================================================
def render_method():
    html = head(
        "Method — The REAL Election Integrity",
        "How this site verifies claims. Confidence labels, sourcing standards, and the public evidence repository.",
        canonical="/method.html",
    )
    html += HEADER
    html += '''
<div class="container"><div class="breadcrumbs"><a href="/">Home</a> <span class="sep">&rsaquo;</span> <span>Method</span></div></div>
<section style="padding-top:24px;">
  <div class="container container-narrow">
    <div class="section-header"><div class="kicker">Method</div><h2 style="margin-top:0;">How this site verifies claims</h2></div>
    <p style="font-size:1.0625rem;">This is a lawful, public, source-cited fact-check of a public federal dashboard. No systems were bypassed, no non-public data was collected, and no submissions were made to the DOJ or DHS report intakes.</p>

    <h3>Confidence labels</h3>
    <ul style="margin-left:1.5rem;">
      <li><strong>CONFIRMED</strong> &mdash; multiple primary sources agree.</li>
      <li><strong>PROBABLE</strong> &mdash; single strong primary source.</li>
      <li><strong>UNVERIFIED</strong> &mdash; unable to substantiate at time of writing. May become CONFIRMED or CONTRADICTED as verification proceeds.</li>
      <li><strong>CONTRADICTED</strong> &mdash; primary source disagrees with the DOJ dashboard.</li>
    </ul>
    <p>The four Tier 1 structural findings are all CONFIRMED. Individual per-state claims are marked UNVERIFIED until reviewed against docket records, DOJ press releases, and state responses. Verification proceeds in tiers:</p>
    <ul style="margin-left:1.5rem;">
      <li><strong>Tier 1</strong> &mdash; the four templates that account for 156 of 243 rows (<em>complete</em>).</li>
      <li><strong>Tier 2</strong> &mdash; the twelve individual voter-roll lawsuits DOJ itself linked (<em>in progress</em>).</li>
      <li><strong>Tier 3</strong> &mdash; DHS press releases referenced by the dashboard's news column (<em>pending</em>).</li>
      <li><strong>Tier 4</strong> &mdash; DOJ election-monitor deployments across seven states (<em>pending</em>).</li>
      <li><strong>Tier 5</strong> &mdash; remaining unsourced individual claims (<em>pending</em>).</li>
    </ul>

    <h3>Evidence archive</h3>
    <p>Every piece of evidence used on this site is public and versioned at <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity">github.com/TheDreyDossier/REAL-Election-Integrity</a>. That repository contains:</p>
    <ul style="margin-left:1.5rem;">
      <li>A verbatim capture of the DOJ dashboard as of launch (page HTML, headers, JSON dataset, all 51 state pages, D3 map JavaScript).</li>
      <li>A full 243-entry claim inventory catalogued by template and by state.</li>
      <li>Per-template verification memos with citation lists.</li>
      <li>The source of this site itself.</li>
    </ul>

    <h3>Corrections</h3>
    <p>If you believe any fact-check on this site is wrong, incomplete, or missing important context, please <a href="/report-an-error.html">report the error</a>. All corrections are logged in the public commit history.</p>

    <div class="callout callout-warn">
      <h3 style="margin-top:0;">This is not a government website</h3>
      <p style="margin-bottom:0;">The REAL Election Integrity is an independent journalism and civic accountability project by The Drey Dossier. It is not affiliated with, endorsed by, or issued by the U.S. Department of Justice, the Department of Homeland Security, or any federal agency. It reproduces DOJ visual language for the purpose of side-by-side comparison and fact-checking.</p>
    </div>
  </div>
</section>
'''
    html += FOOTER
    return html

# ==========================================================
# REPORT AN ERROR PAGE
# ==========================================================
def render_report_error():
    html = head(
        "Report an Error — The REAL Election Integrity",
        "Correct a fact-check. Add a source. Share context. Every correction is logged in the public commit history.",
        canonical="/report-an-error.html",
    )
    html += HEADER
    html += '''
<div class="container"><div class="breadcrumbs"><a href="/">Home</a> <span class="sep">&rsaquo;</span> <span>Report an Error</span></div></div>
<section style="padding-top:24px;">
  <div class="container container-narrow">
    <div class="section-header"><div class="kicker">Corrections</div><h2 style="margin-top:0;">Report an error</h2></div>
    <p style="font-size:1.0625rem;">If any fact-check on this site is wrong, incomplete, or missing important context, we want to know. Every correction is logged in the public commit history at <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity">github.com/TheDreyDossier/REAL-Election-Integrity</a>.</p>
    <h3>How to submit a correction</h3>
    <ol style="margin-left:1.5rem;">
      <li><strong>Open a GitHub issue.</strong> The fastest path: <a href="https://github.com/TheDreyDossier/REAL-Election-Integrity/issues/new">file an issue</a> describing what's wrong and linking to primary sources.</li>
      <li><strong>Submit a pull request.</strong> If you have a specific edit in mind, open a PR against the relevant verification memo in <span class="text-mono">evidence/verifications/</span>.</li>
      <li><strong>Contact directly.</strong> Reach out via <a href="https://github.com/TheDreyDossier">The Drey Dossier on GitHub</a>.</li>
    </ol>
    <h3>What we especially want</h3>
    <ul style="margin-left:1.5rem;">
      <li>Primary-source documents contradicting anything on this site (docket filings, DOJ press releases, state responses, agency correspondence).</li>
      <li>Context on any individual per-state claim currently marked UNVERIFIED.</li>
      <li>Notice of any changes to the DOJ dashboard. Diffs against our launch-day capture are tracked in the repository.</li>
    </ul>
  </div>
</section>
'''
    html += FOOTER
    return html

# ==========================================================
# Write files
# ==========================================================
(OUT / "index.html").write_text(render_home())
(OUT / "about.html").write_text(render_about())
(OUT / "analysis.html").write_text(render_about())  # alias — the reduction/T1-T4 anchors live here
(OUT / "method.html").write_text(render_method())
(OUT / "report-an-error.html").write_text(render_report_error())

for code in STATES:
    slug = state_slug(code)
    (STATE_OUT / f"{slug}.html").write_text(render_state(code))

# Summary
print(f"Generated:")
print(f"  index.html")
print(f"  about.html / analysis.html")
print(f"  method.html")
print(f"  report-an-error.html")
print(f"  {len(STATES)} state pages under states/")
print(f"")
print(f"Data check:")
print(f"  Total actions: {TOTAL_ACTIONS}")
print(f"  Templated: {TEMPLATED_TOTAL} ({100*TEMPLATED_TOTAL/TOTAL_ACTIONS:.1f}%)")
for k, v in TEMPLATE_COUNTS.items():
    print(f"    {k}: {v}")
print(f"  Future-dated as of {TODAY}: {FUTURE_COUNT}")

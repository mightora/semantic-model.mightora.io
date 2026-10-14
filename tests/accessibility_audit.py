"""Run WCAG-tagged axe-core tests against the standalone edition.

This checks automatable issues, not complete WCAG conformance.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "artifacts" / "accessibility"
OUT.mkdir(parents=True, exist_ok=True)
HTML = (ROOT / "dist/downloads/semantic-model-mapper-offline.html").read_text()
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
SCENARIOS = [
    ("desktop-model", 1440, 900),
    ("desktop-high-contrast", 1440, 900),
    ("desktop-relationships", 1440, 900),
    ("desktop-visual-lineage", 1440, 900),
    ("mobile-model", 390, 844),
]
results_by_state = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    try:
        for name, width, height in SCENARIOS:
            page = browser.new_page(viewport={"width": width, "height": height})
            try:
                page.set_content(HTML, wait_until="load")
                page.locator("#diagramSvg g[data-table]").first.wait_for(timeout=10000)
                if name == "desktop-high-contrast":
                    page.locator("#highContrastToggle").click()
                elif name == "desktop-relationships":
                    page.locator("#tabRelationships").click()
                elif name == "desktop-visual-lineage":
                    page.locator("#tabVisuals").click()
                    page.locator("#visualList button").nth(2).click()
                result = Axe().run(page, options={"runOnly": {"type": "tag", "values": TAGS}})
                violations = result.response.get("violations", [])
                (OUT / (name + ".json")).write_text(json.dumps(result.response, indent=2))
                results_by_state.append({
                    "scenario": name, "viewport": [width, height],
                    "violations": [{
                        "id": v["id"], "impact": v.get("impact"), "help": v.get("help"),
                        "nodes": [{
                            "target": n.get("target"), "failureSummary": n.get("failureSummary")
                        } for n in v.get("nodes", [])]
                    } for v in violations]
                })
                print(f"{name}: {len(violations)} violated rules", flush=True)
                for v in violations:
                    print(f"  [{v.get('impact')}] {v['id']}: {v.get('help')}", flush=True)
                    for n in v.get("nodes", [])[:5]:
                        print(f"    {n.get('target')}: {str(n.get('failureSummary'))[:180]}", flush=True)
            finally:
                page.close()
    finally:
        browser.close()

total = sum(len(s["violations"]) for s in results_by_state)
summary = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "engine": "axe-core via axe-playwright-python 0.1.8",
    "tagged_wcag_rules": TAGS,
    "scope": "Standalone offline application; tested states listed below",
    "certifies_wcag_conformance": False,
    "total_violated_rules": total,
    "scenarios": results_by_state
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2))
lines = [
    "# Automated accessibility audit", "",
    "Automatable WCAG 2.0 / 2.1 / 2.2 A & AA checks using axe-core.",
    "This does not certify WCAG conformance; manual testing is required.", "",
    "| State | Violated rules |", "| --- | ---: |"
]
for s in results_by_state:
    lines.append("| " + s["scenario"] + " | " + str(len(s["violations"])) + " |")
lines.extend(["", "Total violated rules across states: " + str(total)])
(OUT / "summary.md").write_text("\n".join(lines))
if total:
    raise SystemExit(f"Accessibility check failed: {total} violated rules. Download the GitHub Actions artifact for details.")
print("PASS: no axe-core WCAG A/AA rule violations in tested states.")

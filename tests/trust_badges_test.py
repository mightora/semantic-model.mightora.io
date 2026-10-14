"""Prevent unverified quality badges from shipping."""
from pathlib import Path
from html.parser import HTMLParser

root = Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text()
class ProofBadges(HTMLParser):
    def __init__(self):
        super().__init__(); self.seen=False; self.href=None; self.badges=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="section" and a.get("class")=="trust-strip outer":self.seen=True
        if self.seen and tag=="a":self.href=a.get("href")
        if self.seen and tag=="img":
            self.badges.append((self.href,a.get("src"),a.get("alt")))
    def handle_endtag(self,tag):
        if tag=="a":self.href=None
        if tag=="section" and self.seen:self.seen=False
p=ProofBadges();p.feed(html)
assert len(p.badges)==4,p.badges
repo="https://github.com/mightora/semantic-model.mightora.io"
for name in ("pages.yml","accessibility.yml","codeql.yml"):
    href=repo+"/actions/workflows/"+name
    assert (root/".github"/"workflows"/name).is_file()
    matches=[x for x in p.badges if x[0]==href]
    assert len(matches)==1 and matches[0][1]==href+"/badge.svg?branch=main", matches
    assert matches[0][2],name
licenseHref=repo+"/blob/main/LICENSE"
lic=[x for x in p.badges if x[0]==licenseHref]
assert len(lic)==1
assert lic[0][1]=="https://img.shields.io/github/license/mightora/semantic-model.mightora.io?label=licence"
assert (root/"LICENSE").read_text().startswith("MIT License")
assert all(src.startswith(("https://github.com/mightora/semantic-model.mightora.io/actions/workflows/","https://img.shields.io/github/license/mightora/semantic-model.mightora.io")) for href,src,alt in p.badges)
assert "A successful scan does not certify security or WCAG conformance." in html
print("PASS: genuine workflow and GitHub-derived licence badge sources")

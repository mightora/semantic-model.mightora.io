#!/usr/bin/env python3
"""Reproducible stdlib release builder: GitHub Pages + self-contained file:// edition."""
from __future__ import annotations
import base64,html,json,re,shutil,zipfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'
LOGO=ROOT/'assets'/'mightora-logo.png'
URL='https://raw.githubusercontent.com/mightora/mightora.io/main/static/images/mightoraIoLogo4-200x900.png'

def official_logo():
    if LOGO.exists() and LOGO.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
        return 'data:image/png;base64,'+base64.b64encode(LOGO.read_bytes()).decode('ascii'), True
    # Build CI retrieves the official logo into assets/ before this script runs.
    # This CSS wordmark is a network-free fallback for development builds only.
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="200" viewBox="0 0 900 200"><rect width="900" height="200" fill="#ffffff"/><text x="18" y="139" font-family="Arial,Helvetica,sans-serif" font-weight="800" font-size="134" fill="#173a4c">MIGHTORA</text></svg>'
    return 'data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode(), False

def compile():
    if DIST.exists():shutil.rmtree(DIST)
    (DIST/'downloads').mkdir(parents=True)
    (DIST/'src').mkdir()
    (DIST/'assets').mkdir()
    shutil.copy(ROOT/'src'/'styles.css',DIST/'src'/'styles.css')
    for n in ('core.js','app.js'):shutil.copy(ROOT/'src'/n,DIST/'src'/n)
    shutil.copy(ROOT/'assets'/'favicon.svg',DIST/'assets'/'favicon.svg')
    samples={n:json.loads((ROOT/'examples'/f'{n}.json').read_text()) for n in ('retail','service')}
    sample_js='\n<script>window.SAMPLE_MODELS='+json.dumps(samples,separators=(',',':')).replace('</','<\\/')+';</script>\n'
    base=(ROOT/'index.html').read_text()
    base=base.replace('  <script src="src/core.js"></script>',sample_js+'  <script src="src/core.js"></script>')
    # Exact edition availability is established only once this script creates both downloads.
    online=base.replace('  <script src="src/core.js"></script>','  <script>window.MIGHTORA_DOWNLOADS_AVAILABLE=true;</script>\n  <script src="src/core.js"></script>')
    (DIST/'index.html').write_text(online)
    logo,official=official_logo()
    offline=re.sub(r'\s*<!-- ONLINE_SHARED_START -->.*?<!-- ONLINE_SHARED_END -->','',base,flags=re.S)
    offline=re.sub(r'\s*<!-- ONLINE_SHARED_SCRIPTS_START -->.*?<!-- ONLINE_SHARED_SCRIPTS_END -->','',offline,flags=re.S)
    # The footer web component is not registered in the standalone offline edition.
    offline=offline.replace(' yaml-url="https://cdn.jsdelivr.net/gh/mightora/shared-ui@main/footer.yaml"','')
    offline=re.sub(r'\s*<!-- ONLINE_FOOTER_PATCH_START -->.*?<!-- ONLINE_FOOTER_PATCH_END -->','',offline,flags=re.S)
    offline=offline.replace('<link rel="stylesheet" href="src/styles.css">','<style>\n'+(ROOT/'src'/'styles.css').read_text().replace('</style>','<\\/style>')+'\n</style>')
    offline=offline.replace('<script src="src/core.js"></script>','<script>\n'+(ROOT/'src'/'core.js').read_text().replace('</script>','<\\/script>')+'\n</script>')
    offline=offline.replace('<script src="src/app.js"></script>','<script>\n'+(ROOT/'src'/'app.js').read_text().replace('</script>','<\\/script>')+'\n</script>')
    offline=offline.replace('https://raw.githubusercontent.com/mightora/mightora.io/main/static/images/mightoraIoLogo4-200x900.png',logo)
    # The author biography remains; remote profile images are removed from the offline edition.
    offline=re.sub(r'<img\s+src="https://(?:techtweedie\.github\.io|raw\.githubusercontent\.com/TechTweedie)[^>]*>', '',offline)
    # On offline file:// the fallback header is kept; no remote shared-ui registered elements.
    offline=offline.replace('<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">','<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,'+base64.b64encode((ROOT/'assets'/'favicon.svg').read_bytes()).decode()+'">')
    offline=offline.replace('<link rel="canonical" href="https://semantic-model.mightora.io/">','')
    offline=offline.replace('<title>Semantic Model Mapper','<title>Offline Semantic Model Mapper')
    offline=offline.replace('<meta name="robots" content="index, follow">','<meta name="robots" content="noindex, nofollow">')
    offline=offline.replace('<meta name="theme-color"','<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data:; font-src data:; connect-src \'none\'; object-src \'none\'; base-uri \'none\'; form-action \'none\'">\n  <meta name="theme-color"')
    offline=offline.replace(sample_js,sample_js+'<script>window.MIGHTORA_OFFLINE=true;</script>')
    # Download buttons in the offline HTML are not meaningful when detached from the ZIP.
    offline=offline.replace('href="downloads/semantic-model-mapper-offline.html" download','href="#privacy"').replace('href="downloads/semantic-model-mapper-offline.zip" download','href="#privacy"')
    offline=re.sub(r'<div class="offline-actions">.*?</div></section>', '<div class="offline-actions"><div><strong>You are running the standalone offline edition.</strong><p>All app processing is local to this file. There are no application network requests.</p></div></div></section>', offline,flags=re.S)
    # Online quality badges are remote SVG images; the file:// edition must never load them.
    offline=re.sub(r'<div class="trust-links" id="trustLinks">.*?</div>',
                   '<div class="trust-links" id="trustLinks"><a href="https://github.com/mightora/semantic-model.mightora.io">Public source on GitHub ↗</a><a href="https://github.com/mightora/semantic-model.mightora.io/blob/main/LICENSE">MIT licence ↗</a></div>',
                   offline,flags=re.S)
    # External anchor hrefs are user-initiated navigation only. If clicked, the browser may open the web.
    target=DIST/'downloads'/'semantic-model-mapper-offline.html'
    target.write_text(offline)
    info=(ROOT/'README.md').read_text()
    license=(ROOT/'LICENSE').read_text()
    with zipfile.ZipFile(DIST/'downloads'/'semantic-model-mapper-offline.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.write(target,'index.html');z.writestr('README.md',info);z.writestr('LICENSE',license)
    manifest={'official_logo_embedded':official,'zip_contains_current_build':True,'offline_size':target.stat().st_size,'online_entrypoint':'index.html','offline_entrypoint':'downloads/semantic-model-mapper-offline.html'}
    (DIST/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Built dist/',json.dumps(manifest))
if __name__=='__main__':compile()

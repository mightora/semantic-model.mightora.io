import json,re,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
html=(root/'dist'/'downloads'/'semantic-model-mapper-offline.html').read_text()
assert 'Offline Edition – No Internet Connection Required' in html
assert "connect-src 'none'" in html
assert 'https://cdn.jsdelivr.net/' not in html
assert '<script src=' not in html
assert '<link rel="stylesheet" href=' not in html
assert 'MapperCore' in html
assert 'window.SAMPLE_MODELS=' in html
assert '<mightora-footer' in html
assert 'role="group" aria-label="Relationship diagram' in html
assert 'id="inspector" class="inspector-content" tabindex="0" role="region"' in html
assert '<div class="footer-bottom">' in html
assert 'class="footer-fallback"' in html
assert 'aria-label="Mightora website links"' in html
assert html.count('class="footer-brand"')==3
assert html.count('class="footer-col"')==3
assert 'https://mightora.io/privacy-policy/' in html
assert 'fallback-footer' not in html
assert 'Semantic Model Mapper by' in html
assert 'class="author-avatar-fallback offline-show"' in html
assert 'class="author-blog-fallback offline-show"' in html
assert 'ian-tweedie-sq2.png' not in html
assert 'class="author-area"' in html
assert 'src="https:' not in html, 'offline images should never fetch remotely'
assert 'logo-light="data:image/' in html
assert not re.search(r'<(iframe|script|img|link)[^>]+(?:src|href)="https:',html,re.I)
online=(root/'dist'/'index.html').read_text()
assert '<mightora-footer yaml-url=' in online
assert 'Open source. Independently verifiable.' in online
assert 'Built by TechTweedie' in online
assert 'class="footer-fallback"' in online
assert online.count('class="footer-col"')==3
assert online.count('class="footer-brand"')==3
assert 'https://mightora.io/$2/$3' in online
assert 'fallback-footer' not in online
assert (root/'dist'/'index.html').is_file()
with zipfile.ZipFile(root/'dist'/'downloads'/'semantic-model-mapper-offline.zip') as z:
    assert {'index.html','LICENSE','README.md'} <= set(z.namelist())
    assert z.read('index.html')==html.encode()
assert json.loads((root/'dist'/'build-manifest.json').read_text())['zip_contains_current_build']
print('PASS: offline content, CSP, no remote script/css/images, ZIP parity and online build')

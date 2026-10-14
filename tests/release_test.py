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
assert 'src="https:' not in html, 'offline images should never fetch remotely'
assert 'logo-light="data:image/' in html
assert not re.search(r'<(iframe|script|img|link)[^>]+(?:src|href)="https:',html,re.I)
assert (root/'dist'/'index.html').is_file()
with zipfile.ZipFile(root/'dist'/'downloads'/'semantic-model-mapper-offline.zip') as z:
    assert {'index.html','LICENSE','README.md'} <= set(z.namelist())
    assert z.read('index.html')==html.encode()
assert json.loads((root/'dist'/'build-manifest.json').read_text())['zip_contains_current_build']
print('PASS: offline content, CSP, no remote script/css/images, ZIP parity and online build')

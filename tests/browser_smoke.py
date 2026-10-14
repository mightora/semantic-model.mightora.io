"""Functional browser smoke test. Requires playwright and a Chromium installation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
html=(ROOT/'dist/downloads/semantic-model-mapper-offline.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None,args=["--no-sandbox"])
    desktop=browser.new_page(viewport={'width':1440,'height':900},accept_downloads=True)
    errors=[];requests=[]
    desktop.on('pageerror',lambda e:errors.append(str(e)))
    desktop.on('request',lambda request:requests.append(request.url))
    desktop.set_content(html)
    assert desktop.locator('#tableCount').inner_text()=='6'
    assert desktop.locator('#diagramSvg g[data-table]').count()==6
    desktop.locator('#tabVisuals').click()
    desktop.locator('#visualList button').nth(2).click()
    assert desktop.locator('#inspector .inspect-name').inner_text()=='Sales by Product Category'
    assert desktop.locator('#diagramSvg text').filter(has_text='REPORT VISUAL').count()==1
    with desktop.expect_download() as record:
        desktop.locator('#exportMermaid').click()
    assert record.value.suggested_filename.endswith('.mmd')
    with desktop.expect_download() as record:
        desktop.locator('#exportSvg').click()
    assert record.value.suggested_filename.endswith('.svg')
    desktop.locator('#sampleSelect').select_option('service')
    assert desktop.locator('#tableCount').inner_text()=='5'
    desktop.locator('#fileInput').set_input_files({'name':'model.json','mimeType':'application/json','buffer':b'{"name":"Tiny","tables":[{"name":"A","columns":[{"name":"id"}]}],"relationships":[]} '})
    assert desktop.locator('#tableCount').inner_text()=='1'
    assert desktop.locator('#datasetPill').inner_text()=='Local file'
    assert not errors,errors
    # The standalone edition retains the full footer even without the shared CDN.
    assert desktop.locator('mightora-footer .footer-fallback').is_visible()
    assert desktop.locator('mightora-footer .footer-col').count()==3
    assert desktop.locator('mightora-footer .footer-brand').count()==3
    # Simulate what shared-ui does after its YAML fetch: prepend generated columns
    # and brand strip before the original fallback and copyright bar.
    desktop.evaluate("""() => {const e=document.querySelector('mightora-footer');
      const original=e.innerHTML;e.innerHTML='<div class="container"><div class="footer-main"><div class="footer-col">Shared navigation</div></div></div><div class="container"><div class="footer-brands"><a class="footer-brand">Shared brands</a></div></div>'+original;
    }""")
    assert not desktop.locator('mightora-footer .footer-fallback').is_visible()
    assert desktop.locator('mightora-footer > .container > .footer-main').is_visible()
    assert not requests,requests
    mobile=browser.new_page(viewport={'width':390,'height':844})
    mobile_errors=[];mobile.on('pageerror',lambda e:mobile_errors.append(str(e)))
    mobile.set_content(html)
    assert mobile.locator('#tableCount').inner_text()=='6'
    assert mobile.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')==0
    assert mobile.locator('mightora-footer .footer-fallback').is_visible()
    assert mobile.locator('mightora-footer .footer-col').count()==3
    assert not mobile_errors,mobile_errors
    print('PASS: interactive browser smoke, exports, local import, zero network, desktop/mobile')
    browser.close()

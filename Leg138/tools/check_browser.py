"""Exercise a packaged browse.html over file://, without a web server or API."""
import argparse
import csv
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright


def check(path, executable, flags):
    result = {}
    with sync_playwright() as manager:
        browser=manager.chromium.launch(executable_path=executable,headless=True,args=flags)
        page=browser.new_page(viewport={'width':1100,'height':900})
        script_errors=[]
        page.on('pageerror',lambda error:script_errors.append(str(error)))
        page.goto(path.resolve().as_uri())
        assert page.locator('.detail h2').inner_text()=='Site 846'
        selections=page.locator('nav button[data-id]').evaluate_all('(items)=>items.map(el=>el.dataset.id)')
        assert len(selections)==23
        for selection in selections:
            page.locator(f'nav button[data-id="{selection}"]').click()
            assert page.locator('h2').inner_text()==('Site '+selection if selection.isdigit() else selection)
            if selection.isdigit():
                filled=page.locator('#carbonRows tbody tr').count()
                page.locator('#cfilter').select_option('all')
                all_records=page.locator('#carbonRows tbody tr').count()
                assert all_records>0
                for img in page.locator('article img').all():
                    img.scroll_into_view_if_needed()
                    img.evaluate('(image)=>image.decode()')
                page.get_by_text('离线读本站科学与作业正文',exact=True).click()
                assert len(page.locator('details[open] .source').all())>=2
                repeat=page.locator('#carbonateRepeats')
                repeat.locator('summary').click()
                repeats=repeat.locator('tbody tr').count()
                assert repeats>0
                if selection=='853':
                    assert repeats==24 and '0.83' in repeat.inner_text()
                if selection=='850':
                    assert '随盘原表' in repeat.inner_text()
                if selection=='854':
                    assert (filled,all_records)==(0,63)
                if selection=='846':
                    assert (filled,all_records)==(147,318)
                    page.locator('#cfilter').select_option('filled')
                    with page.expect_download() as dl:page.locator('#download').click()
                    with dl.value.path().open(encoding='utf-8-sig') as exported:
                        assert len(list(csv.DictReader(exported)))==147
                result[selection]={'nonempty_org_c':filled,'source_rows':all_records,'repeat_sample_rows':repeats}
            urls=page.locator('a').evaluate_all('(anchors)=>anchors.map(el=>el.href)')
            for u in urls:
                if u.startswith('file:'):assert Path(unquote(urlsplit(u).path)).is_file(),(selection,u)
        for val in ('EEQ-4A','852B','IR11.T10','GRAPE','isotope'):
            page.locator('#query').fill(val)
            assert page.locator('#results .result').count()>0,val
        page.locator('#query').fill('EEQ-4A')
        page.locator('#results button').first.click()
        assert page.locator('.detail h2').inner_text()=='EEQ-4A'
        page.locator('#query').fill('carbonate')
        page.locator('#api').click()
        assert page.locator('#apiHint a').get_attribute('href')=='http://127.0.0.1:8138/api/search?q=carbonate'
        page.goto(path.resolve().as_uri()+'#852')
        assert page.locator('h2').inner_text()=='Site 852'
        page.set_viewport_size({'width':390,'height':820})
        page.goto(path.resolve().as_uri()+'#846')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        assert not script_errors,script_errors
        browser.close()
    return result


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('html',type=Path)
    a.add_argument('--executable',help='custom headless Chromium binary')
    a.add_argument('--args-json',type=Path,help='optional array of Chromium launch arguments')
    args=a.parse_args()
    flags=json.loads(args.args_json.read_text()) if args.args_json else []
    print(json.dumps(check(args.html,args.executable,flags),indent=2))

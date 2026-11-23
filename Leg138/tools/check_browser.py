"""Exercise a packaged browse.html over file://, without a web server or API."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from playwright.sync_api import sync_playwright


def check_portal(page, folder):
    page.context.set_offline(True)
    page.locator('.catalogCta').click()
    page.wait_for_url('**/catalog.html*')
    totals=page.evaluate('Object.fromEntries(Object.entries(data).map(([k,v])=>[k,v.length]))')
    assert totals=={'books':76,'ir':911,'sr':809,'photos':593,'smear':1156,'geo':191},totals
    page.locator('[data-tab="ir"]').click()
    page.locator('#kind').select_option('table')
    assert '/ 259' in page.locator('#status').inner_text()
    local_files=set(page.evaluate("""()=>[
      ...data.books.map(r=>'publication/chapters/'+r[0]+'.pdf'),
      ...data.ir.flatMap(r=>r[7].map(v=>v[1])),
      ...data.sr.flatMap(r=>[r[8],r[9]].filter(Boolean)),
      'publication/chapters/index.html','ir/core/edition2_print/data/leg138_geography.geojson'
    ]"""))
    for item in local_files:
        if not (folder/item).is_file():
            raise FileNotFoundError(folder/item)
    with (folder/'publication/chapters/catalog.csv').open(encoding='utf-8-sig') as f:
        book_files=list(csv.DictReader(f))
    compact_pages={r['doc_id']:int(r['reading_pages']) for r in book_files}
    assert page.evaluate('Object.fromEntries(data.books.map(r=>[r[0],r[7]]))')==compact_pages
    for book in book_files:
        pdf=folder/'publication/chapters'/book['local_path']
        assert pdf.stat().st_size==int(book['bytes'])
        assert hashlib.sha256(pdf.read_bytes()).hexdigest()==book['sha256']
    assert len(book_files)==76
    loaded=page.evaluate("""async()=>{
      const all=await Promise.all(['all',...Array.from({length:11},(_,i)=>String(i+844))].map(shard));
      const tables=Object.assign({},...all.map(x=>x.tables));
      for(const r of data.ir.filter(r=>r[3]==='table'))
        if(!tables[r[0]]||tables[r[0]][1].length!==r[6]||!tables[r[0]][0].length)throw Error(r[0]);
      return [Object.keys(tables).length,all.reduce((n,x)=>n+Object.values(x.regions).flat().length,0),
        all.reduce((n,x)=>n+Object.values(x.smear).flat().length,0)]
    }""")
    assert loaded==[259,12989,25194],loaded
    for s in map(str,range(844,855)):
        page.locator('#site').select_option(s)
        for tab,kind in [('ir','table'),('sr',''),('photos',''),('smear','')]:
            page.locator('[data-tab="'+tab+'"]').click()
            if kind:page.locator('#kind').select_option(kind)
            assert page.locator('#hits .record').count()>0,(s,tab)
            page.locator('#hits .record').first.click()
            if tab=='sr':
                assert '站点关联证据' in page.locator('#record').inner_text()
            else:
                with page.expect_download() as incoming:page.locator('#csvExport').click()
                with incoming.value.path().open(encoding='utf-8-sig') as f:
                    records=list(csv.DictReader(f))
                assert records,(s,tab)
                if tab=='photos':assert all(r['roi_id'].startswith(s) and len(r['jpeg_sha256'])==64 for r in records)
                if tab=='smear':assert all(r['row_id'].startswith('S'+s) and r['x0_pt'] for r in records)
    page.locator('[data-tab="geo"]').click()
    page.locator('#site').select_option('854')
    page.locator('#ageSlider').fill('4')
    assert '原题站号冲突' in page.locator('#record').inner_text()
    assert page.locator('#geoMap svg circle').count()==0
    page.locator('#site').select_option('844')
    assert '仅纬度' in page.locator('#record').inner_text()
    page.locator('#site').select_option('851')
    assert page.locator('#geoMap svg circle').count()==1
    page.locator('#ageSlider').fill('-1')
    assert page.locator('#geoMap svg circle').count()==5
    page.locator('#site').select_option('')
    page.locator('[data-tab="photos"]').click();page.locator('#find').fill('138-846D-20X')
    assert page.locator('#record h2').inner_text()=='846D20X'
    page.locator('#csvExport').wait_for()
    page.locator('[data-tab="ir"]').click();page.locator('#find').fill('IR18.T12')
    assert page.locator('#record h2').inner_text()=='IR18.T12'
    page.locator('#csvExport').wait_for()
    page.locator('[data-tab="sr"]').click();page.locator('#find').fill('SR.C06.FIGURE11')
    assert page.locator('#record h2').inner_text()=='SR.C06.FIGURE11'
    page.locator('[data-tab="books"]').click();page.locator('#find').fill('IR.C11')
    assert 'publication/chapters/IR.C11.pdf' in page.locator('#record a').first.get_attribute('href')
    for book in book_files:
        page.goto((folder/'catalog.html').as_uri()+'#tab=books&id='+quote(book['doc_id']))
        assert page.locator('#record h2').inner_text()==book['doc_id']
        target=(folder/'publication/chapters'/book['local_path']).as_uri()
        with page.context.expect_event('response',predicate=lambda value:value.url==target) as response:
            with page.context.expect_page() as popup:
                page.locator('#record a').first.click()
        assert response.value.status==200,target
        popup.value.close()
    page.locator('#rebuild summary').click()
    assert 'build_edition.py' in page.locator('#rebuild').inner_text()
    page.set_viewport_size({'width':390,'height':820})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    return {'record_counts':totals,'named_IR_tables':loaded[0],'photo_regions':loaded[1],
            'smear_cells':loaded[2],'station_filters_and_CSV_downloads_checked':11,
            'local_paths_checked':len(local_files),'compact_PDFs_opened_and_hash_checked':len(book_files),'network_disabled':True}


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
        page.set_viewport_size({'width':1100,'height':900})
        result['whole_leg']=check_portal(page,path.resolve().parent)
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

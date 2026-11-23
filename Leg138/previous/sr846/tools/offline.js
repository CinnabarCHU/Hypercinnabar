/* The standalone edition uses exactly the same UI as the local JSON API. */
window.standaloneArchive=true;
const archivePack=JSON.parse(document.getElementById('archive-pack').textContent);
const hydrated=new Map();
async function inflateJson(data){
 const bytes=Uint8Array.from(atob(data),c=>c.charCodeAt(0));
 const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
 return JSON.parse(await new Response(stream).text());
}
async function unpack(key){
 if(!hydrated.has(key))hydrated.set(key,inflateJson(archivePack[key]));return hydrated.get(key);
}
function asUrl(content,type){return URL.createObjectURL(new Blob([content],{type}))}
const figureUrl=asUrl(Uint8Array.from(atob(archivePack.figure),c=>c.charCodeAt(0)),'application/pdf');
const archiveLocations=['row_no','source_line','source_line_end','print_page','panel','print_row','pdf_y_pt','record_note','raw_literal'];
async function archiveGet(path){
 const req=new URL(path,'http://archive.invalid/');const p=req.pathname;const q=req.searchParams;
 const m=await unpack('metadata');
 if(p==='/api/chapters')return m.chapters;
 if(p==='/api/items')return m.items.filter(x=>!q.has('chapter')||x.chapter==q.get('chapter'));
 if(p==='/api/datasets')return m.datasets.filter(x=>!q.has('item')||x.item===q.get('item'));
 if(p==='/api/reviews')return m.reviews.filter(r=>Array.from(q).every(([k,v])=>String(r[k])===v));
 if(p==='/api/relations')return m.relations.filter(r=>!q.has('item')||[r.child,r.parent].includes(q.get('item')));
 const [_,api,mode,k,id]=p.split('/');if(api!=='api'||!['row','rows'].includes(mode))throw Error('未知查询');
 const ds=m.datasets.find(x=>x.dataset===k);if(!ds)throw Error('未知数据版本');
 const f=m.fields[k],columns=archiveLocations.concat(f.map(t=>t.field)),source=m.sources[ds.source];
 const packed=await unpack(k),query=(q.get('q')||'').toLowerCase();
 let matched=mode==='row'?packed.filter(r=>r[0]===Number(id)):query?packed.filter(r=>r.slice(8).some(v=>String(v??'').toLowerCase().includes(query))):packed;
 const start=Math.max(0,Number(q.get('offset'))||0),limit=Number(q.get('limit'))||25;
 const item=m.items.find(x=>x.item===ds.item);
 const rows=matched.slice(start,start+limit).map(raw=>{const r=Object.fromEntries(columns.map((k,i)=>[k,raw[i]]));r.source_url=source.url+(r.print_page?'#page='+(r.print_page-item.page_from+item.pdf_page_from):'');return r});
 return {dataset:ds,source,fields:f,total:matched.length,offset:start,rows};
}
function csvValue(x){const v=String(x??'');return /[",\r\n]/.test(v)?'"'+v.replaceAll('"','""')+'"':v}
function standaloneLink(ev){
 const link=ev.target.closest('a');if(!link)return;const s=link.getAttribute('href')||'';
 if(s==='/figure.pdf'){ev.preventDefault();window.open(figureUrl,'_blank');return}
 if(s==='/api'){ev.preventDefault();document.getElementById('record').innerHTML='<section class="paper"><h2>JSON 与 CSV</h2><p>选择一行可下载该记录的 JSON。表头上方可导出当前查询的 CSV。</p><p>本地 HTTP 接口随主包提供。运行 <code>python app.py</code> 后打开 <code>http://127.0.0.1:8460/api</code>。</p></section>';document.getElementById('record').scrollIntoView();return}
 if(!s.startsWith('/csv/')&&!s.startsWith('/api/row/'))return;
 ev.preventDefault();(async()=>{let url,name;
  if(s.startsWith('/csv/')){const req=new URL(s,'http://archive.invalid/');const k=req.pathname.split('/')[2];const t=await archiveGet('/api/rows/'+k+'?limit=1000000&q='+encodeURIComponent(req.searchParams.get('q')||''));const cols=archiveLocations.concat(t.fields.map(x=>x.field));url=asUrl([cols.join(','),...t.rows.map(r=>cols.map(k=>csvValue(r[k])).join(','))].join('\r\n')+'\r\n','text/csv;charset=utf-8');name=k+'.csv'}
  else{const t=await archiveGet(s);url=asUrl(JSON.stringify(t,null,2),'application/json;charset=utf-8');name=t.dataset.dataset+'-'+t.rows[0].row_no+'.json'}
  const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
 })().catch(e=>{document.getElementById('error').textContent=e.message});
}
document.addEventListener('click',standaloneLink,true);

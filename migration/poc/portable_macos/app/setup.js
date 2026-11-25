window.acyclePortable.onStatus(text=>{document.getElementById('status').textContent=text;});
document.getElementById('retry').onclick=()=>window.acyclePortable.retry();
document.getElementById('logs').onclick=()=>window.acyclePortable.logs();

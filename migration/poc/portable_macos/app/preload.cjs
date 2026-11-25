const {contextBridge,ipcRenderer}=require('electron');
if(location.protocol==='file:') contextBridge.exposeInMainWorld('acyclePortable',{
  onStatus:(fn)=>ipcRenderer.on('portable-status',(_event,message)=>fn(message)),
  retry:()=>ipcRenderer.send('portable-retry'),
  logs:()=>ipcRenderer.send('portable-logs')
});

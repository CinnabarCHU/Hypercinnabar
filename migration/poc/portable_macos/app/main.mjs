import {app,BrowserWindow,dialog,Menu,ipcMain,shell} from 'electron';
import {spawn,execFileSync} from 'node:child_process';
import {createWriteStream,existsSync,readFileSync,writeFileSync,unlinkSync} from 'node:fs';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID} from 'node:crypto';
import {paths,prepare,environment,writeJson,configure,loadConnection,hostArgs,readReadyUrl,matlabExpression} from './portable.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const bundle=resolve(process.resourcesPath,'..','..');
let p, earlyError;
try {
  let root=process.env.ACYCLE_PORTABLE_ROOT || dirname(bundle);
  if(!existsSync(join(root,'portable.json')) && process.platform==='darwin'){
    // App Translocation may hide the original app's sibling workspace.
    // A native picker runs before Chromium creates any profile or cache.
    root=execFileSync('/usr/bin/osascript',['-e',
      'POSIX path of (choose folder with prompt "请选择同时含 Acycle Harness.app、Workspace 和 portable.json 的试用文件夹")'],
      {encoding:'utf8'}).trim();
  }
  p=paths(root,process.resourcesPath);
  prepare(p);
  // Set Chromium storage before app.ready or any BrowserWindow/session exists.
  for(const [key,value] of Object.entries({userData:p.electron,sessionData:p.electron,
    logs:p.logs,crashDumps:join(p.state,'crashes')})) app.setPath(key,value);
  app.setAppLogsPath(p.logs);
  app.setPath('temp',p.tmp);
} catch(error) { earlyError=error; }
let win,host,matlab,busy=false,quitting=false,ready=false,stopFile,hostOrigin;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const setup=join(here,'setup.html');
const status=text=>{if(win && !win.isDestroyed())win.webContents.send('portable-status',text);};

async function stopHost(){
  if(!host || host.exitCode!==null)return;
  const owned=host;
  owned.kill('SIGTERM');
  for(let i=0;i<40 && owned.exitCode===null;i++)await sleep(100);
  if(owned.exitCode===null)owned.kill('SIGKILL');
  host=null;
}

async function selectMatlab(){
  const pref=join(p.state,'launcher.json');
  let selected='/Applications/MATLAB_R2024a.app';
  try{selected=JSON.parse(readFileSync(pref,'utf8')).matlabApp;}catch{}
  if(!selected || !existsSync(join(selected,'bin','matlab'))){
    const answer=await dialog.showOpenDialog(win,{title:'选择 MATLAB R2024a.app',defaultPath:'/Applications',
      properties:['openFile','openDirectory'],filters:[{name:'MATLAB',extensions:['app']}]});
    if(answer.canceled)throw new Error('尚未选择 MATLAB。点击“重新连接”继续。');
    selected=answer.filePaths[0];
    if(!existsSync(join(selected,'bin','matlab')))throw new Error('请选择包含 bin/matlab 的 MATLAB 应用。');
  }
  writeJson(pref,{matlabApp:selected});
  return join(selected,'bin','matlab');
}

async function launchMatlab(){
  const executable=await selectMatlab();
  const token=randomUUID();
  stopFile=join(p.state,'control',token+'.stop');
  const generated=join(p.workspace,'generated');
  const connection=join(generated,'connection.json');
  try{unlinkSync(connection);}catch{}
  const env=environment(p);
  delete env.DEEPSEEK_API_KEY;
  Object.assign(env,{ACYCLE_PORTABLE_WORKSPACE:p.workspace,ACYCLE_PORTABLE_STATE:p.state,
    ACYCLE_PORTABLE_STOP:stopFile,ACYCLE_PORTABLE_TOKEN:token});
  const log=createWriteStream(join(p.logs,'matlab-launch.log'),{flags:'a',mode:0o600});
  matlab=spawn(executable,['-desktop','-nosplash','-r',matlabExpression(join(p.workspace,'portable_bootstrap.m'))],
    {cwd:p.workspace,env,stdio:['ignore','pipe','pipe']});
  matlab.stdout.pipe(log,{end:false});matlab.stderr.pipe(log,{end:false});
  let failed;matlab.on('error',e=>{failed=e;});matlab.once('close',()=>log.end());
  status('正在启动 MATLAB R2024a 与 Acycle 滤波窗口……\n这会打开一个专用于此次试用的 MATLAB 进程。');
  for(let i=0;i<480;i++){
    if(quitting)throw new Error('正在退出');
    if(failed)throw failed;
    try{
      const receipt=JSON.parse(readFileSync(join(generated,'portable-host.json'),'utf8'));
      if(receipt.token===token){
        if(receipt.status==='failed')throw new Error(receipt.message);
        if(receipt.status==='ready')return loadConnection(p);
      }
    }catch(e){if(e.code!=='ENOENT' && !(e instanceof SyntaxError))throw e;}
    await sleep(500);
  }
  throw new Error('MATLAB 在四分钟内未完成启动。请检查 MATLAB 的许可证、Java 和所需工具箱，并查看 matlab-launch.log。');
}

async function launchHost(connection){
  configure(p,connection);
  await stopHost();
  status('Acycle 已连接，正在启动 DeepSeek Harness 聊天界面……');
  const log=createWriteStream(join(p.logs,'harness.log'),{flags:'a',mode:0o600});
  host=spawn(p.node,hostArgs(p),{cwd:join(p.workspace,'study'),env:environment(p),stdio:['ignore','pipe','pipe']});
  const owned=host;
  const url=await new Promise((ok,no)=>{
    let buffer='';
    const timer=setTimeout(()=>no(new Error('Harness 启动超时，请查看 harness.log。')),90000);
    const finish=(error,value)=>{clearTimeout(timer);error?no(error):ok(value);};
    owned.on('error',e=>finish(e));
    owned.once('exit',code=>finish(new Error(`Harness 提前退出（${code}），请查看 harness.log。`)));
    for(const stream of [owned.stdout,owned.stderr])stream.on('data',chunk=>{
      const text=chunk.toString();
      log.write(text.replace(/(http:\/\/127\.0\.0\.1:\d+\/)\S*/g,'$1[session-link]'));
      buffer=(buffer+text).slice(-128000);
      const found=readReadyUrl(buffer);if(found)finish(null,found);
    });
  });
  owned.once('close',()=>log.end());
  hostOrigin=new URL(url).origin;
  await win.loadURL(url);ready=true;
  owned.once('exit',()=>{if(!quitting){ready=false;void win.loadFile(setup).then(()=>status('Harness 已停止。请检查日志后重新连接。'));}});
  return url;
}

async function start(){
  if(busy || quitting)return;busy=true;
  try{
    if(win.webContents.getURL()!==new URL('file://'+setup).href)await win.loadFile(setup);
    let connection;
    try{connection=loadConnection(p);}catch{}
    if(!connection){
      if(stopFile && existsSync(join(p.workspace,'generated','portable-host.json')))
        throw new Error('本次 MATLAB 窗口已关闭或启动未完成。请退出本应用后重新打开；这会重新建立独立会话。');
      connection=await launchMatlab();
    }
    await launchHost(connection);
  }catch(error){status(error.message);}
  finally{busy=false;}
}

app.whenReady().then(async()=>{
  if(earlyError){await dialog.showMessageBox({type:'error',title:'Acycle Harness',message:earlyError.message});app.quit();return;}
  if(!app.requestSingleInstanceLock()){app.quit();return;}
  win=new BrowserWindow({width:1200,height:850,minWidth:860,minHeight:600,title:'Acycle Harness',
    webPreferences:{preload:join(here,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
  win.webContents.setWindowOpenHandler(({url})=>{
    if(/^https?:\/\//.test(url))void shell.openExternal(url);
    return {action:'deny'};
  });
  win.webContents.on('will-navigate',(event,url)=>{
    if(url.startsWith('file:') || (hostOrigin && new URL(url).origin===hostOrigin))return;
    event.preventDefault();if(/^https?:\/\//.test(url))void shell.openExternal(url);
  });
  win.webContents.session.setPermissionRequestHandler((_webContents,_permission,callback)=>callback(false));
  win.webContents.session.on('will-download',(_event,item)=>{
    // User-requested downloads default to the portable workspace.
    item.setSaveDialogOptions({defaultPath:join(p.workspace,'study',item.getFilename())});
  });
  const local=event=>event.sender===win.webContents && event.senderFrame?.url.startsWith('file:');
  ipcMain.on('portable-retry',event=>{if(local(event))void start();});
  ipcMain.on('portable-logs',event=>{if(local(event))void shell.openPath(p.logs);});
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    {label:'Acycle Harness',submenu:[{label:'退出 Acycle Harness',accelerator:'Cmd+Q',click:()=>app.quit()}]},
    {label:'编辑',submenu:[{role:'undo'},{role:'redo'},{type:'separator'},{role:'cut'},{role:'copy'},{role:'paste'},{role:'selectAll'}]},
    {label:'试用',submenu:[{label:'重新连接 Acycle',click:()=>void start()},
      {label:'打开工作区',click:()=>void shell.openPath(join(p.workspace,'study'))},
      {label:'打开日志',click:()=>void shell.openPath(p.logs)},
      {label:'重新载入聊天界面',click:()=>win.reload()}]}
  ]));
  app.on('second-instance',()=>{win.show();win.focus();});
  await win.loadFile(setup);
  if(process.env.ACYCLE_PORTABLE_SMOKE==='1'){
    try{
      const c={protocol:1,workspace:join(p.workspace,'study'),guiSession:join(p.tmp,'smoke-session'),matlabExecutable:'/not-used'};
      await launchHost(c);
      await sleep(4000);
      const ui=await win.webContents.executeJavaScript('({text:document.body.innerText,buttons:document.querySelectorAll("#root button").length,title:document.title})');
      if(ui.text.length<30 || ui.buttons<1 || !ui.title.includes('Harness'))throw new Error('Harness chat UI did not render');
      writeFileSync(join(p.logs,'harness-window.png'),(await win.webContents.capturePage()).toPNG());
      writeJson(join(p.logs,'app-smoke.json'),{status:'passed',platform:process.platform,arch:process.arch,
        electron:process.versions.electron,uiTextLength:ui.text.length,uiButtons:ui.buttons,hostReady:ready});
      app.quit();
    }catch(e){writeJson(join(p.logs,'app-smoke.json'),{status:'failed',message:e.message});app.quit();}
  }else await start();
});

app.on('window-all-closed',()=>app.quit());
app.on('before-quit',event=>{
  if(quitting)return;
  event.preventDefault();quitting=true;
  void(async()=>{
    await stopHost();
    if(stopFile){
      writeFileSync(stopFile,'stop\n',{mode:0o600});
      // Only the dedicated MATLAB process owns this unique stop-file timer.
      for(let i=0;i<50 && existsSync(stopFile);i++)await sleep(100);
    }
    app.quit();
  })();
});

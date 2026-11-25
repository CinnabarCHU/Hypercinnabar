import {existsSync, mkdirSync, readFileSync, writeFileSync, renameSync} from 'node:fs';
import {join, resolve, delimiter} from 'node:path';
import {pathToFileURL} from 'node:url';

export function paths(root, resources) {
  root = resolve(root); resources = resolve(resources);
  if (!existsSync(join(root, 'portable.json')) || !existsSync(join(root, 'Workspace', 'start_local_demo.m')))
    throw new Error('请保持 Acycle Harness.app、Workspace 和 portable.json 在同一个解压文件夹中。请先把整个文件夹移到桌面，再打开应用。');
  return {root, resources, workspace:join(root,'Workspace'), state:join(root,'State'),
    home:join(root,'State','harness'), tmp:join(root,'State','tmp'),
    logs:join(root,'State','logs'), electron:join(root,'State','electron'),
    runtime:join(resources,'runtime'), python:join(resources,'python','bin','python3'),
    node:join(resources,'node','bin','node')};
}

export function prepare(p) {
  for (const dir of [p.state,p.home,p.tmp,p.logs,p.electron,join(p.state,'control'),
    join(p.state,'matlab-prefs'),join(p.state,'cache'),join(p.state,'config'),join(p.state,'data')])
    mkdirSync(dir,{recursive:true,mode:0o700});
}

export function environment(p, inherited=process.env) {
  const env = {...inherited, DSH_HOME:p.home, DSH_TELEMETRY_DISABLED:'1',
    PYTHONNOUSERSITE:'1', PYTHONDONTWRITEBYTECODE:'1',
    TMPDIR:p.tmp+'/', TMP:p.tmp, TEMP:p.tmp,
    XDG_CACHE_HOME:join(p.state,'cache'), XDG_CONFIG_HOME:join(p.state,'config'),
    XDG_DATA_HOME:join(p.state,'data'), NPM_CONFIG_CACHE:join(p.state,'cache','npm'),
    PIP_CACHE_DIR:join(p.state,'cache','pip'), MATLAB_PREFDIR:join(p.state,'matlab-prefs'),
    PATH:[join(p.resources,'node','bin'),join(p.resources,'python','bin'),'/usr/bin','/bin','/usr/sbin','/sbin'].join(delimiter)};
  // Inherited Python/Node injection must not redirect the bundled interpreters.
  for (const k of ['PYTHONHOME','PYTHONPATH','NODE_PATH','NODE_OPTIONS','ELECTRON_RUN_AS_NODE']) delete env[k];
  return env;
}

export function writeJson(file, value) {
  mkdirSync(resolve(file,'..'),{recursive:true,mode:0o700});
  writeFileSync(file+'.tmp',JSON.stringify(value,null,2)+'\n',{mode:0o600});
  renameSync(file+'.tmp',file);
}

export function configure(p, connection) {
  const profile=join(p.home,'profiles','web');
  const plugin={id:'acycle-native',name:pathToFileURL(join(p.runtime,'node_modules','dsh-acycle','index.mjs')).href,
    config:{python:p.python,workspace:connection.workspace,guiSession:connection.guiSession,
      matlabExecutable:connection.matlabExecutable}};
  const persona='You are the Acycle GUI research assistant. This portable demonstration connects to the already open MATLAB window. For this window use acycle_gui_inspect, acycle_gui_open, acycle_gui_update and acycle_gui_events. Inspect before editing, retain physical units, and use window_id plus expected_revision. Do not call batch menu tools: this distribution is configured for the live GUI. Filter and image_profile are supported live features; other Acycle menus remain available to the user in MATLAB. When the user draws an image profile, ask them to choose Finish profile and send a follow-up message, then query events. No automatic completion wake-up is implemented. Never report an action as successful without its actual tool result.';
  const patch=[
    {id:'agent-preset-registry',config:{default:'acycle'}},
    {id:'hmr',disabled:true},
    {id:'desktop-product-telemetry',disabled:true},
    {id:'preset-standard',disabled:true},{id:'preset-ptc',disabled:true},
    {id:'preset-minimal',disabled:true},{id:'preset-cordis',disabled:true},
    {insert:[{id:'preset-acycle',name:'@deepseek-ai/dsh-agent-preset',config:{
      id:'acycle',name:'Acycle MATLAB',description:'与当前 Acycle 窗口协作',order:0,plugins:[
        {id:'acycle-persona',name:'@deepseek-ai/dsh-persona',config:{prefix:persona}},plugin,
        {id:'acycle-skills',name:'@deepseek-ai/dsh-tool-skill'},
        {id:'acycle-files',name:'@deepseek-ai/dsh-tool-fs',config:{read:true,readImage:true,write:false,edit:false}},
        {id:'acycle-present',name:'@deepseek-ai/dsh-tool-present'},
        {id:'acycle-questions',name:'@deepseek-ai/dsh-tool-ask-user'}
      ]}}]}
  ];
  writeJson(join(profile,'package.json'),{name:'acycle-portable-profile',private:true,
    dsh:{profile:{bundles:['@deepseek-ai/dsh-base','@deepseek-ai/dsh-web-app']}}});
  writeJson(join(profile,'cordis.patch.yml'),patch);
  writeJson(join(p.workspace,'generated','harness-plugin.json'),plugin);
  return plugin;
}

export function loadConnection(p) {
  const c=JSON.parse(readFileSync(join(p.workspace,'generated','connection.json'),'utf8'));
  if(c.protocol!==1 || resolve(c.workspace)!==join(p.workspace,'study') ||
    !existsSync(join(c.guiSession,'session.json'))) throw new Error('Acycle 窗口连接已关闭，请重新启动本次试用。');
  return c;
}

export function hostArgs(p) {
  return [join(p.runtime,'node_modules','@deepseek-ai','dsh','lib','bin.js'),
    '--profile','web','--host','127.0.0.1','--port','0','--no-open'];
}

export function readReadyUrl(text) {
  const match=text.match(/dsh web: (http:\/\/127\.0\.0\.1:\d+\/[^\s]*)/);
  if (!match) return null;
  const url=new URL(match[1]);
  return url.hostname==='127.0.0.1' && url.protocol==='http:' ? url.href : null;
}

export function matlabExpression(file) {
  return `run('${file.replaceAll("'","''")}')`;
}

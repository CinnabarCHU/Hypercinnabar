function fig = start_local_demo()
% Open the packaged synthetic example in the native Acycle desktop.
root = fileparts(mfilename('fullpath'));
required = {'pmtm','hilbert','norminv','imshow','improfile'};
missing = required(cellfun(@(name)exist(name,'file')==0,required));
if ~isempty(missing)
    error('Acycle:Demo:Toolboxes', ...
        'Missing functions: %s. Install Signal Processing, Statistics and Machine Learning, and Image Processing Toolbox.',strjoin(missing,', '));
end
addpath(fullfile(root,'acycle'));
setup_acycle();
workspace = fullfile(root,'study');
generated = fullfile(root,'generated');
if ~isfolder(generated), mkdir(generated); end
setenv('ACYCLE_LOG_DIR',fullfile(generated,'journals'));
fig = ac(workspace);
h = acgui.state(fig);
h.popupmenu1.Value = find(strcmp(cellstr(h.popupmenu1.String),'m'));
invoke(h.popupmenu1);
h.listbox_acmain.Value = find(strcmp(cellstr(h.listbox_acmain.String),'series.csv'));
invoke(h.menu_filter);
session = acgui.share(fig);
executable = fullfile(matlabroot,'bin','matlab');
if ispc, executable = [executable,'.exe']; end
connection = struct('protocol',1,'guiSession',session,'workspace',workspace, ...
    'matlabExecutable',executable);
file = fullfile(generated,'connection.json');
accore.io('writeText',[file,'.tmp'],jsonencode(connection),'UTF-8');
movefile([file,'.tmp'],file,'f');
fprintf('\nAcycle local demo is ready. Keep the desktop open.\n');
fprintf('From a system terminal in this folder, run:\n');
fprintf('  python3 local_test.py prepare\n  python3 local_test.py check\n');
fprintf('On Windows use py -3 in place of python3.\n');
fprintf('Connection settings: %s\n',file);
end

function invoke(control)
callback = control.Callback;
if iscell(callback)
    feval(callback{1},control,[],callback{2:end});
else
    callback(control,[]);
end
end

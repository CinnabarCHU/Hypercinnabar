function folder = share(fig)
% Connect only this desktop. The native GUI services typed JSON requests locally.
if nargin<1, fig = acgui.desktop(); end
key = 'AcycleHarnessSession';
if isappdata(fig,key)
    session = getappdata(fig,key); folder = session.folder; return;
end
base = java.io.File(tempdir);
attrs = javaArray('java.nio.file.attribute.FileAttribute',double(isunix));
if isunix
    perm = java.nio.file.attribute.PosixFilePermissions.fromString('rwx------');
    attrs(1) = java.nio.file.attribute.PosixFilePermissions.asFileAttribute(perm);
end
folder = char(java.nio.file.Files.createTempDirectory(base.toPath(),'acycle-gui-',attrs).toString());
clock = timer('ExecutionMode','fixedSpacing','Period',.15,'BusyMode','drop','TimerFcn',@(~,~)poll(folder));
try
    writeText(fullfile(folder,'session.json'),jsonencode(struct('protocol',1)));
    listener = addlistener(fig,'ObjectBeingDestroyed',@(~,~)dispose(clock,folder));
    setappdata(fig,key,struct('folder',folder,'clock',clock,'listener',listener));
    start(clock);
catch err
    if isappdata(fig,key), rmappdata(fig,key); end
    dispose(clock,folder); rethrow(err);
end
end

function poll(folder)
requests = dir(fullfile(folder,'*.request.json'));
for k = 1:min(numel(requests),4)
    name = requests(k).name;
    id = regexp(name,'^([0-9a-f]{32})\.request\.json$','tokens','once');
    if isempty(id), continue; end
    prefix = fullfile(folder,id{1});
    working = [prefix,'.working'];
    [claimed,~] = movefile(fullfile(folder,name),working);
    if ~claimed, continue; end
    try
        q = jsondecode(fileread(working));
        validateattributes(q.deadline,{'numeric'},{'real','scalar','finite'});
        if q.deadline<posixtime(datetime('now','TimeZone','UTC'))
            error('Acycle:GUI:Expired','This desktop request expired before it started.');
        end
        value = acgui.live(q.action,jsonencode(q.arguments));
        reply = struct('ok',true,'json',value);
    catch err
        reply = struct('ok',false,'identifier',err.identifier,'message',err.message);
    end
    if ~isfolder(folder), return; end
    tmp = [prefix,'.reply.tmp'];
    writeText(tmp,jsonencode(reply));
    movefile(tmp,[prefix,'.reply.json']);
    delete(working);
end
end

function writeText(file,value)
[fid,msg] = fopen(file,'w','n','UTF-8');
if fid<0, error('Acycle:GUI:File','%s',msg); end
finish = onCleanup(@()fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s',value);
end

function dispose(clock,folder)
if isvalid(clock), stop(clock); delete(clock); end
if isfolder(folder), rmdir(folder,'s'); end
end

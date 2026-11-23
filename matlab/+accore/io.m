function value = io(action,varargin)
% Shared workspace, series and exchange I/O. The workspace preference is per user.
switch char(action)
case 'workspace'
    value = getpref('AcyclePoC','Workspace',pwd);
    if ~isfolder(value), value = pwd; end
case 'chdir'
    [ok,info] = fileattrib(varargin{1});
    if ~ok || ~info.directory, error('Acycle:IO:Directory','Directory does not exist.'); end
    value = info.Name;
    setpref('AcyclePoC','Workspace',value);
case 'workspaceFile'
    folder = fullfile(prefdir,'AcyclePoC');
    if ~isfolder(folder), mkdir(folder); end
    value = fullfile(folder,'ac_pwd.txt');
    if ~isfile(value), accore.io('writeText',value,accore.io('workspace')); end
case 'list'
    entries = dir(varargin{1});
    entries = entries(~ismember({entries.name},{'.','..'}));
    if isempty(entries), value = entries; return; end
    order = varargin{2};
    fields = {'name','name','datenum','datenum','bytes','bytes'};
    directions = {'ascend','descend','ascend','descend','ascend','descend'};
    t = sortrows(struct2table(entries),fields{order},directions{order});
    value = table2struct(t);
case 'read'
    value = load(varargin{1});
case 'readImage'
    value = imread(varargin{1});
case 'imageInfo'
    value = imfinfo(varargin{1});
case 'readText'
    value = fileread(varargin{1});
case 'writeMatrix'
    dlmwrite(varargin{:});
    value = varargin{1};
case 'writeText'
    [fid,msg] = fopen(varargin{1},'w','n',varargin{3:end});
    if fid < 0, error('Acycle:IO:Open','%s',msg); end
    closeFile = onCleanup(@()fclose(fid)); %#ok<NASGU>
    fprintf(fid,'%s',varargin{2});
    value = varargin{1};
case 'save'
    file = char(varargin{1}); session = varargin{2};
    folder = fileparts(file); if isempty(folder), folder = pwd; end
    tmp = [tempname(folder),'.mat'];
    cleanup = onCleanup(@()discard(tmp)); %#ok<NASGU>
    [session,records] = accore.exchange(session);
    save(tmp,'session','records','-v7.3');
    [ok,msg] = movefile(tmp,file,'f');
    if ~ok, error('Acycle:IO:Save','%s',msg); end
    value = file;
case 'load'
    payload = load(varargin{1});
    value = payload.session;
    if isfield(payload,'records'), value = accore.exchange(value,payload.records); end
otherwise
    error('Acycle:IO:Action','Unknown I/O operation %s.',action);
end
end

function discard(p)
if isfile(p), delete(p); end
end

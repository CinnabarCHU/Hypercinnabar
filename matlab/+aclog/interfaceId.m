function value = interfaceId(id,lookupOnly)
% Register integer journals; one warning per session for automatic console journals.
if nargin < 2, lookupOnly = false; end
directory = getenv('ACYCLE_LOG_DIR');
if isempty(directory), directory = fullfile(prefdir,'acycle-calls'); end
if isequal(id,'register') && nargin==1
    root = fullfile(directory,'registered');
    if ~isfolder(root), mkdir(root); end
    n = floor((now-datenum(1970,1,1))*86400000); %#ok<TNOW,DATNM>
    while true
        folder = fullfile(root,sprintf('%.0f',n));
        [ok,msg,code] = mkdir(folder);
        if ~ok, error('Acycle:Logger:Directory','%s',msg); end
        if isempty(code), break; end
        n = n+1;
    end
    acCreateJournalFile(fullfile(folder,'events.jsonl'));
    value = n;
    return
end
if isnumeric(id) && isscalar(id) && isreal(id) && isfinite(id) && ...
        id>=1 && id<=flintmax && id==fix(id)
    file = fullfile(directory,'registered',sprintf('%.0f',id),'events.jsonl');
elseif ischar(id) || (isstring(id) && isscalar(id))
    file = char(id);
else
    file = '';
end
if ~isempty(file) && isfile(file)
    [ok,info] = fileattrib(file);
    if ok, value = info.Name; return; end
end
if lookupOnly, error('Acycle:Logger:UnknownId','No journal registered for this id.'); end
value = aclog.newId(directory);
acCreateJournalFile([value,'.console']);
persistent warned
if isempty(warned)
    warning('Acycle:Logger:AutomaticId','No registered id supplied. The console records include the new journal path.');
    warned = true;
end
end

function acCreateJournalFile(file)
[fid,msg] = fopen(file,'wb');
if fid<0, error('Acycle:Logger:Open','%s',msg); end
if fclose(fid)~=0, error('Acycle:Logger:Write','Unable to create %s.',file); end
end

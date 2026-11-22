function id = newId(directory)
% Reserve a separate directory and journal for one invocation.
if nargin == 0
    directory = getenv('ACYCLE_LOG_DIR');
    if isempty(directory), directory = fullfile(prefdir, 'acycle-calls'); end
end
if ~isfolder(directory)
    [ok, msg] = mkdir(directory);
    if ~ok, error('Acycle:Logger:Directory', '%s', msg); end
end
[ok, info] = fileattrib(directory);
if ~ok, error('Acycle:Logger:Directory', 'Cannot locate the log directory.'); end
while true
    folder = tempname(info.Name);
    [ok, msg, msgid] = mkdir(folder);
    if ~ok, error('Acycle:Logger:Directory', '%s', msg); end
    if isempty(msgid), break; end
end
id = fullfile(folder, 'events.jsonl');
[fid, msg] = fopen(id, 'wb');
if fid < 0, error('Acycle:Logger:Open', '%s', msg); end
if fclose(fid) ~= 0, error('Acycle:Logger:Write', 'Cannot close %s.', id); end
end

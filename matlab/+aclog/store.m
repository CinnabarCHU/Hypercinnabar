function ref = store(id, field, value)
% Store an immutable MATLAB value next to its journal. References relocate with it.
[directory, name, ext] = fileparts(id);
ref = [name, ext, '.', field, '.mat'];
dest = fullfile(directory, ref);
if isfile(dest), error('Acycle:Logger:Reuse', 'Snapshot already exists: %s', dest); end
staging = [dest, '.tmp'];
cleanup = onCleanup(@() discard(staging));
if exist('OCTAVE_VERSION', 'builtin')
    save(staging, 'value', '-mat7-binary');
else
    save(staging, 'value', '-v7.3');
end
[ok, msg] = movefile(staging, dest);
if ~ok, error('Acycle:Logger:Write', '%s', msg); end
end

function discard(file)
if isfile(file), delete(file); end
end

function logger(id, attr, info)
% Append one public method event to an existing call journal.
if ~isfile(id)
    error('Acycle:Logger:UnknownId', 'Unknown call journal: %s', id);
end
if ~(isstruct(info) && isscalar(info))
    error('Acycle:Logger:InvalidInfo', 'info must be a scalar struct.');
end
record = struct('attr', attr, 'info', info);
encoded = unicode2native([jsonencode(record), char(10)], 'UTF-8');
[fid, message] = fopen(id, 'ab');
if fid < 0, error('Acycle:Logger:Open', '%s', message); end
try
    n = fwrite(fid, encoded, 'uint8');
catch err
    fclose(fid);
    rethrow(err);
end
closed = fclose(fid);
if n ~= numel(encoded) || closed ~= 0
    error('Acycle:Logger:Write', 'Incomplete journal write to %s.', id);
end
end

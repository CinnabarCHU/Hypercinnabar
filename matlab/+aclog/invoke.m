function [retval, id] = invoke(op, params, id, implementation)
% Call one method role, preserving the original MATLAB exception.
if isempty(id), id = aclog.newId(); end
if ~isfile(id), error('Acycle:Logger:UnknownId', 'Unknown call journal: %s', id); end
[ok, file] = fileattrib(id);
if ~ok, error('Acycle:Logger:UnknownId', 'Unknown call journal: %s', id); end
id = file.Name;
lock = [id, '.lock'];
[ok, msg, msgid] = mkdir(lock);
if ~ok || ~isempty(msgid), error('Acycle:Logger:Busy', 'Cannot claim call journal %s: %s', id, msg); end
cleanup = onCleanup(@() rmdir(lock));
entry = dir(id);
if entry.bytes ~= 0, error('Acycle:Logger:Reuse', 'This id already has an invocation.'); end
ref = aclog.store(id, 'params', params);
aclog.store(id, 'rng', rng);
logger(id, 'init', struct('op', op, 'params', ref));
try
    if nargout(implementation) == 2
        [retval, status] = implementation(params);
    else
        retval = implementation(params);
        status = 'done';
    end
    if ~any(strcmp(status, {'incomplete','cancelled','done'}))
        error('Acycle:Logger:Status', 'Invalid completion status: %s', status);
    end
    if isempty(retval)
        ref = [];
    else
        ref = aclog.store(id, 'retval', retval);
    end
catch err
    logger(id, 'error', struct('logging', err.message, 'details', struct()));
    logger(id, 'fin', struct('status', 'cancelled', 'retval', []));
    rethrow(err);
end
logger(id, 'fin', struct('status', status, 'retval', ref));
end

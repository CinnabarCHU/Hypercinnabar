function [retval, id] = invoke(op, params, id, implementation)
% Call one method role, preserving the original MATLAB exception.
if isstruct(id) && isscalar(id) && isfield(id,'acycleParentJournal')
    parent = id.acycleParentJournal;
    if ~ischar(parent) || ~isfile(parent) || ~isfolder([parent,'.lock'])
        error('Acycle:Logger:Parent','Expected an active enclosing menu invocation.');
    end
    [retval,status,caught] = runMethod(implementation,params);
    if ~isempty(caught), rethrow(caught); end
    id = struct('status',status);
    return
end
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
    % The expression is constant. The method is a function handle, and parameters stay as MATLAB values.
    transcript = evalc('[retval, status, caught] = runMethod(implementation, params);');
    if ~isempty(strtrim(transcript))
        logger(id,'msg',struct('logging',transcript,'details',struct()));
        if ~isfile([id,'.console']), fprintf('%s',transcript); end
    end
    if ~isempty(caught), rethrow(caught); end
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

function [result, status, caught] = runMethod(implementation, params)
result = [];
status = 'done';
caught = [];
try
    if nargout(implementation) == 2
        [result, status] = implementation(params);
    else
        result = implementation(params);
    end
catch err
    caught = err;
end
end

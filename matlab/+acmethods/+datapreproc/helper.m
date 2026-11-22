function [retval, id] = helper(params, id)
% datapreproc.helper parameters: target qwarn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/datapreproc.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('datapreproc-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'target', 'qwarn'}, 1, @legacyDefaults);
end

function values = legacyDefaults(target, qwarn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/datapreproc.m:L2-L2
if nargin<2; qwarn=1; end
%% End copied source
values = struct();
if exist('target', 'var'), values.target = target; end
if exist('qwarn', 'var'), values.qwarn = qwarn; end
end

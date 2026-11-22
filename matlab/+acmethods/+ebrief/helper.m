function [retval, id] = helper(params, id)
% ebrief.helper parameters: X dim a.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ebrief.m#L12
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ebrief-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'X', 'dim', 'a'}, 1, @legacyDefaults);
end

function values = legacyDefaults(X, dim, a)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ebrief.m:L12-L20
if nargin > 4
    error('Too many input arguments')
end
if nargin < 3
    a = 0;
if nargin < 2
    dim = 1;
end
end
%% End copied source
values = struct();
if exist('X', 'var'), values.X = X; end
if exist('dim', 'var'), values.dim = dim; end
if exist('a', 'var'), values.a = a; end
end

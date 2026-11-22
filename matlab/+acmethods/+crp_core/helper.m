function [retval, id] = helper(params, id)
% crp_core.helper parameters: x y m tau e method normFlag.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/crp_core.m#L20
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('crp_core-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'x', 'y', 'm', 'tau', 'e', 'method', 'normFlag'}, 1, @legacyDefaults);
end

function values = legacyDefaults(x, y, m, tau, e, method, normFlag)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/recurrence/crp_core.m:L20-L25
if nargin < 7 || isempty(normFlag), normFlag = 'norm'; end
if nargin < 6 || isempty(method),   method   = 'rr';        end
if nargin < 5 || isempty(e),        e        = 0.1;        end
if nargin < 4 || isempty(tau),      tau      = 1;          end
if nargin < 3 || isempty(m),        m        = 1;          end
if nargin < 2 || isempty(y),        y        = x;          end
%% End copied source
values = struct();
if exist('x', 'var'), values.x = x; end
if exist('y', 'var'), values.y = y; end
if exist('m', 'var'), values.m = m; end
if exist('tau', 'var'), values.tau = tau; end
if exist('e', 'var'), values.e = e; end
if exist('method', 'var'), values.method = method; end
if exist('normFlag', 'var'), values.normFlag = normFlag; end
end

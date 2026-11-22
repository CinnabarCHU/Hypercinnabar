function [retval, id] = helper(params, id)
% crp_pdist.helper parameters: x w ws theiler_window lmin plotn threshold method_use normFlag m tau.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/crp_pdist.m#L12
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('crp_pdist-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'x', 'w', 'ws', 'theiler_window', 'lmin', 'plotn', 'threshold', 'method_use', 'normFlag', 'm', 'tau'}, 1, @legacyDefaults);
end

function values = legacyDefaults(x, w, ws, theiler_window, lmin, plotn, threshold, method_use, normFlag, m, tau)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/recurrence/crp_pdist.m:L12-L25
if nargin < 11 || isempty(tau), tau = 1; end
if nargin < 10 || isempty(m),   m   = 1; end
if nargin < 9 || isempty(normFlag),        normFlag = 'norm'; end
if nargin < 8 || isempty(method_use),      method_use = 'rr'; end
if nargin < 7 || isempty(threshold),       threshold = 0.10; end
if nargin < 6 || isempty(plotn),           plotn = 0; end
if nargin < 5 || isempty(lmin),            lmin = 2; end
if nargin < 4 || isempty(theiler_window),  theiler_window = 1; end
if nargin < 3 || isempty(ws),              ws = 1; end

Nx = size(x,1);
if nargin < 2 || isempty(w)
    w = floor(0.5 * Nx);
end
%% End copied source
values = struct();
if exist('x', 'var'), values.x = x; end
if exist('w', 'var'), values.w = w; end
if exist('ws', 'var'), values.ws = ws; end
if exist('theiler_window', 'var'), values.theiler_window = theiler_window; end
if exist('lmin', 'var'), values.lmin = lmin; end
if exist('plotn', 'var'), values.plotn = plotn; end
if exist('threshold', 'var'), values.threshold = threshold; end
if exist('method_use', 'var'), values.method_use = method_use; end
if exist('normFlag', 'var'), values.normFlag = normFlag; end
if exist('m', 'var'), values.m = m; end
if exist('tau', 'var'), values.tau = tau; end
end

function [retval, id] = helper(params, id)
% cohac.helper parameters: x y sr window winsize nooverlap alpha qplot.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/cohac.m#L34
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('cohac-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'x', 'y', 'sr', 'window', 'winsize', 'nooverlap', 'alpha', 'qplot'}, 2, @legacyDefaults);
end

function values = legacyDefaults(x, y, sr, window, winsize, nooverlap, alpha, qplot)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/cohac.m:L34-L40
if nargin < 8; qplot = 2; end
if nargin < 7; alpha = 0.1; end  % 90% confidence level
if nargin < 6; nooverlap = []; end
if nargin < 5; winsize = []; end
if nargin < 4; window = 'hamming'; end
if nargin < 3; sr = 1; end
if nargin < 2; return; end
%% End copied source
values = struct();
if exist('x', 'var'), values.x = x; end
if exist('y', 'var'), values.y = y; end
if exist('sr', 'var'), values.sr = sr; end
if exist('window', 'var'), values.window = window; end
if exist('winsize', 'var'), values.winsize = winsize; end
if exist('nooverlap', 'var'), values.nooverlap = nooverlap; end
if exist('alpha', 'var'), values.alpha = alpha; end
if exist('qplot', 'var'), values.qplot = qplot; end
end

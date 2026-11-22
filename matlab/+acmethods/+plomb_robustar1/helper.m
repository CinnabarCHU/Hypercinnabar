function [retval, id] = helper(params, id)
% plomb_robustar1.helper parameters: datax timex fmax smoothwin plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/plomb_robustar1.m#L34
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('plomb_robustar1-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'datax', 'timex', 'fmax', 'smoothwin', 'plotn'}, 2, @legacyDefaults);
end

function values = legacyDefaults(datax, timex, fmax, smoothwin, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/plomb_robustar1.m:L34-L36
if nargin < 5; plotn = 0; end
if nargin < 4; smoothwin = 0.2; end
if nargin < 3; fmax = 1/(2 * mean(diff(timex))); end
%% End copied source
values = struct();
if exist('datax', 'var'), values.datax = datax; end
if exist('timex', 'var'), values.timex = timex; end
if exist('fmax', 'var'), values.fmax = fmax; end
if exist('smoothwin', 'var'), values.smoothwin = smoothwin; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

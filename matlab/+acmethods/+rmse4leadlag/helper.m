function [retval, id] = helper(params, id)
% rmse4leadlag.helper parameters: target series ll step timedir plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/rmse4leadlag.m#L32
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rmse4leadlag-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'target', 'series', 'll', 'step', 'timedir', 'plotn'}, 4, @legacyDefaults);
end

function values = legacyDefaults(target, series, ll, step, timedir, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/rmse4leadlag.m:L32-L33
if nargin < 6; plotn = 1; end
if nargin < 5; timedir = 1; end
%% End copied source
values = struct();
if exist('target', 'var'), values.target = target; end
if exist('series', 'var'), values.series = series; end
if exist('ll', 'var'), values.ll = ll; end
if exist('step', 'var'), values.step = step; end
if exist('timedir', 'var'), values.timedir = timedir; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

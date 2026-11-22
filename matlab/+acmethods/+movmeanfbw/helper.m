function [retval, id] = helper(params, id)
% movmeanfbw.helper parameters: data window step halfwindow alpha plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/movmeanfbw.m#L34
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('movmeanfbw-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'window', 'step', 'halfwindow', 'alpha', 'plotn'}, 1, @legacyDefaults);
end

function values = legacyDefaults(data, window, step, halfwindow, alpha, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/movmeanfbw.m:L34-L45
% first column
timestamps = data(:,1);
% max and min of time
tmin = min(timestamps);
tmax = max(timestamps);
tspan = tmax - tmin;

if nargin < 6; plotn = 0; end
if nargin < 5; alpha = 0.05; end
if nargin < 4; halfwindow = 0; end
if nargin < 3; step = median(diff(data(:,1))); end
if nargin < 2; window = 0.3 * (tspan); end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('window', 'var'), values.window = window; end
if exist('step', 'var'), values.step = step; end
if exist('halfwindow', 'var'), values.halfwindow = halfwindow; end
if exist('alpha', 'var'), values.alpha = alpha; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

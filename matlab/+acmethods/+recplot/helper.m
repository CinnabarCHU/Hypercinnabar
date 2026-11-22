function [retval, id] = helper(params, id)
% recplot.helper parameters: x threshold t plotn labelx labely.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/recplot.m#L24
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('recplot-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'x', 'threshold', 't', 'plotn', 'labelx', 'labely'}, 1, @legacyDefaults);
end

function values = legacyDefaults(x, threshold, t, plotn, labelx, labely)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/recurrence/recplot.m:L24-L29
if nargin < 6; labely = 'Value'; end
if nargin < 5; labelx = 'Time'; end
if nargin < 4; plotn = 1; end
if nargin < 3; t = 1:length(x);end
if nargin < 2; threshold = 0.2; end
if nargin < 1; error('Error: no data'); end
%% End copied source
values = struct();
if exist('x', 'var'), values.x = x; end
if exist('threshold', 'var'), values.threshold = threshold; end
if exist('t', 'var'), values.t = t; end
if exist('plotn', 'var'), values.plotn = plotn; end
if exist('labelx', 'var'), values.labelx = labelx; end
if exist('labely', 'var'), values.labely = labely; end
end

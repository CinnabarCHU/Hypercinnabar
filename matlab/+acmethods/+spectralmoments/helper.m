function [retval, id] = helper(params, id)
% spectralmoments.helper parameters: data window step pad srmean smoothmodel padedge.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/spectralmoments.m#L76
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('spectralmoments-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'window', 'step', 'pad', 'srmean', 'smoothmodel', 'padedge'}, 1, @legacyDefaults);
end

function values = legacyDefaults(data, window, step, pad, srmean, smoothmodel, padedge)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L76-L82
if nargin > 7; error('Too many input arguments'); end
if nargin < 7; padedge = 1; end
if nargin < 6; smoothmodel = 'poly'; end
if nargin < 5; srmean = 0;end
if nargin < 4; pad = 5;   end
if nargin < 3; step = data(2,1) - data(1,1); end
if nargin < 2; window = .35 * (data(end,1)-data(1,1));end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('window', 'var'), values.window = window; end
if exist('step', 'var'), values.step = step; end
if exist('pad', 'var'), values.pad = pad; end
if exist('srmean', 'var'), values.srmean = srmean; end
if exist('smoothmodel', 'var'), values.smoothmodel = smoothmodel; end
if exist('padedge', 'var'), values.padedge = padedge; end
end

function [retval, id] = helper(params, id)
% tanerhilbertML.helper parameters: data fc fl fh c.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/tanerhilbertML.m#L27
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('tanerhilbertML-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'fc', 'fl', 'fh', 'c'}, 4, @legacyDefaults);
end

function values = legacyDefaults(data, fc, fl, fh, c)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/tanerhilbertML.m:L27-L27
if nargin < 5; c = 10^12; end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('fc', 'var'), values.fc = fc; end
if exist('fl', 'var'), values.fl = fl; end
if exist('fh', 'var'), values.fh = fh; end
if exist('c', 'var'), values.c = c; end
end

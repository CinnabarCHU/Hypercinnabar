function [retval, id] = helper(params, id)
% zeropad2.helper parameters: data win padding.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/zeropad2.m#L17
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('zeropad2-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'win', 'padding'}, 1, @legacyDefaults);
end

function values = legacyDefaults(data, win, padding)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/zeropad2.m:L17-L18
if nargin < 3; padding = 1; end
if nargin < 2; win = 0.35 * abs(data(end,1) - data(1,1)); end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('win', 'var'), values.win = win; end
if exist('padding', 'var'), values.padding = padding; end
end

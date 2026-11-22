function [retval, id] = analyzer(params, id)
% MovingMean.analyzer parameters: data smooth_v.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7379
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MovingMean-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
smooth_v = p.smooth_v;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7379-L7379
                data(:,2) = movemean(data(:,2),smooth_v);
%% End copied source
r = struct();
r.data = data;
end

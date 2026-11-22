function [retval, id] = helper(params, id)
% MovingMean.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7373
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MovingMean-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7373-L7373
            defaultans = {'3'};
%% End copied source
smooth_v=str2double(defaultans{1});
r = struct();
r.data = data;
r.smooth_v = smooth_v;
end

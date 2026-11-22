function [retval, id] = helper(params, id)
% MovingGaussian.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7719
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MovingGaussian-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7719-L7719
            defaultans = {'4'};
%% End copied source
window=str2double(defaultans{1});
r = struct();
r.data = data;
r.window = window;
end

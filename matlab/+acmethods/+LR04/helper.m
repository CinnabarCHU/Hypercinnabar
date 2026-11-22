function [retval, id] = helper(params, id)
% LR04.helper parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3053
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LR04-v1.0/helper', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3053-L3053
defaultans = {'0','5320'};
%% End copied source
t1=str2double(defaultans{1});
t2=str2double(defaultans{2});
r = struct();
r.t1 = t1;
r.t2 = t2;
end

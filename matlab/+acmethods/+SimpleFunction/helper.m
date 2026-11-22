function [retval, id] = helper(params, id)
% SimpleFunction.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3708
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SimpleFunction-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3708-L3708
            defaultans = {'1','0','1','0'};
%% End copied source
a=str2double(defaultans{1});
b=str2double(defaultans{2});
c=str2double(defaultans{3});
d=str2double(defaultans{4});
r = struct();
r.data = data;
r.a = a;
r.b = b;
r.c = c;
r.d = d;
end

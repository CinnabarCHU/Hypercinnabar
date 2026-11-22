function [retval, id] = analyzer(params, id)
% SimpleFunction.analyzer parameters: data a b c d.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3717
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SimpleFunction-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
a = p.a;
b = p.b;
c = p.c;
d = p.d;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3717-L3718
            data(:,1) = a * data(:,1) + b;
            data(:,2) = c * data(:,2) + d;
%% End copied source
r = struct();
r.data = data;
end

function [retval, id] = analyzer(params, id)
% BootstrapSmooth.analyzer parameters: x y method span bootn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/SmoothBootGUI.m#L155
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('BootstrapSmooth-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
x = p.x;
y = p.y;
method = p.method;
span = p.span;
bootn = p.bootn;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SmoothBootGUI.m:L155-L162
    [meanboot,bootstd,bootprt] = smoothciML(x,y,method,span,bootn);
    data2(:,1) = x;
    data2(:,2) = meanboot - 2*bootstd;
    data2(:,3) = meanboot - bootstd;
    data2(:,4) = meanboot;
    data2(:,5) = meanboot + bootstd;
    data2(:,6) = meanboot + 2*bootstd;
    data1 = [x,bootprt];
%% End copied source
r = struct();
r.data1 = data1;
r.data2 = data2;
r.meanboot = meanboot;
r.bootstd = bootstd;
r.bootprt = bootprt;
end

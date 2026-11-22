function [retval, id] = analyzer(params, id)
% BootstrapSmooth.analyzer parameters: x y method span bootn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/SmoothBootGUI.m#L155
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('BootstrapSmooth-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
x = p.x;
y = p.y;
span = p.span;
method = p.method;
bootn = p.bootn;
q=acmethods.smoothciML.analyzer(struct('X',x,'Y',y,'span',span,'method',method,'bootn',bootn));
meanboot=q.meanboot; bootstd=q.bootstd; bootprt=q.bootprt;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SmoothBootGUI.m:L156-L162
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

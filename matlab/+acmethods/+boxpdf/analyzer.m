function [retval, id] = analyzer(params, id)
% boxpdf.analyzer parameters: X.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/boxpdf.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('boxpdf-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[boxedX, Bx, By] = boxpdf(p.X);
r = struct();
r.boxedX = boxedX;
r.Bx = Bx;
r.By = By;
end

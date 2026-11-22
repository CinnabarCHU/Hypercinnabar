function [retval,id] = analyzer(params,id)
% boxpdf.analyzer parameters: X.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/boxpdf.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('boxpdf-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[boxedX, Bx, By] = boxpdf(p.X);
r = struct();
r.boxedX = boxedX;
r.Bx = Bx;
r.By = By;
end

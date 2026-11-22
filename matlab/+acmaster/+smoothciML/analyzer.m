function [retval,id] = analyzer(params,id)
% smoothciML.analyzer parameters: X Y method span bootn.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/smoothciML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('smoothciML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
X = p.X;
Y = p.Y;
method = p.method;
span = p.span;
bootn = p.bootn;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/smoothciML.m:L35-L42
f = @(xy) smoothci(xy,X,span,method);
yboot2 = bootstrp(bootn,f,[X,Y])';

meanboot = mean(yboot2,2);
bootstd = std(yboot2,0,2);
%percentile
%bootprt = prctile(yboot2, [.5,2.275,15.865,50,84.135,97.725,99.5],2);
bootprt = prctile(yboot2, [0.5,2.5,5,25,50,75,95,97.5,99.5],2);
%% End copied source
r = struct();
r.meanboot = meanboot;
r.bootstd = bootstd;
r.bootprt = bootprt;
end

function [retval,id] = analyzer(params,id)
% rmse4leadlag.analyzer parameters: target series ll step timedir.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/rmse4leadlag.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('rmse4leadlag-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[llgrid, RMSE] = rmse4leadlag(p.target, p.series, p.ll, p.step, p.timedir, 0);
r = struct();
r.llgrid = llgrid;
r.RMSE = RMSE;
end

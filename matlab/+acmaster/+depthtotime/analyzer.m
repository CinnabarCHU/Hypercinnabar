function [retval,id] = analyzer(params,id)
% depthtotime.analyzer parameters: depth agemodel.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/depthtotime.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('depthtotime-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[time, sr] = depthtotime(p.depth, p.agemodel);
r = struct();
r.time = time;
r.sr = sr;
end

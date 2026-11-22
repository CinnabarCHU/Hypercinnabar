function [retval,id] = analyzer(params,id)
% select_interval.analyzer parameters: data t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/select_interval.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('select_interval-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[select_inter] = select_interval(p.data, p.t1, p.t2);
r = struct();
r.select_inter = select_inter;
end

function [retval,id] = analyzer(params,id)
% SamplingGrid.analyzer parameters: coordinate relativeTolerance.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSamplingIsUneven.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SamplingGrid-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
if isempty(p.relativeTolerance), error('Acycle:Method:MissingOption','Supply the sampling tolerance.'); end
[isUneven, info] = acycleSamplingIsUneven(p.coordinate, p.relativeTolerance);
r = struct();
r.isUneven = isUneven;
r.info = info;
end

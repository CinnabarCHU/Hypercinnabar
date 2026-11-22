function [retval,id] = analyzer(params,id)
% Lag1.analyzer parameters: data samplingInterval windowLength.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEvolutionaryRho1.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Lag1-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleEvolutionaryRho1(p.data, p.samplingInterval, p.windowLength);
r = struct();
r.result = result;
r.meta = meta;
end

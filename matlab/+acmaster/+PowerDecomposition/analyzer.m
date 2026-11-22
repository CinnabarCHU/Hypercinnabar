function [retval,id] = analyzer(params,id)
% PowerDecomposition.analyzer parameters: data targetBands options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acyclePowerDecomposition.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PowerDecomposition-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, bandPowers, meta] = acyclePowerDecomposition(p.data, p.targetBands, p.options);
r = struct();
r.result = result;
r.bandPowers = bandPowers;
r.meta = meta;
end

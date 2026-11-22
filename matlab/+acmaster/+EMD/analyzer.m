function [retval,id] = analyzer(params,id)
% EMD.analyzer parameters: data options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEmpiricalModeDecomposition.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EMD-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'method','max_num_imf','max_num_extrema','interpolation'});
if ~strcmpi(p.options.method,'emd'), error('Acycle:EMD:Method','Expected emd options.'); end
[result, meta] = acycleEmpiricalModeDecomposition(p.data, p.options);
r = struct();
r.result = result;
r.meta = meta;
end

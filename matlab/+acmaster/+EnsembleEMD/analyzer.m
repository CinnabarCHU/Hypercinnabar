function [retval,id] = analyzer(params,id)
% EnsembleEMD.analyzer parameters: data options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEmpiricalModeDecomposition.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EnsembleEMD-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'method','max_num_imf','ensemble_count','noise_amplitude','random_seed','progress_fcn','cancel_fcn'});
if ~strcmpi(p.options.method,'eemd'), error('Acycle:EMD:Method','Expected eemd options.'); end
[result, meta] = acycleEmpiricalModeDecomposition(p.data, p.options);
r = struct();
r.result = result;
r.meta = meta;
end

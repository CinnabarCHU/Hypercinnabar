function [retval,id] = helper(params,id)
% EnsembleEMD.helper parameters: data, optional options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEmpiricalModeDecomposition.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EnsembleEMD-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options = struct('method','eemd');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L312-L314
if ~isfield(options,'max_num_imf')
    options.max_num_imf = 10;
end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L330-L332
    if ~isfield(options,'ensemble_count')
        options.ensemble_count = 100;
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L335-L337
    if ~isfield(options,'noise_amplitude')
        options.noise_amplitude = 0.2;
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L340-L342
    if ~isfield(options,'random_seed')
        options.random_seed = 0;
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L345-L350
    if ~isfield(options,'progress_fcn')
        options.progress_fcn = [];
    end
    if ~isfield(options,'cancel_fcn')
        options.cancel_fcn = [];
    end
%% End copied source
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end

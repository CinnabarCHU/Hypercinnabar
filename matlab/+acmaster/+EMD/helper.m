function [retval,id] = helper(params,id)
% EMD.helper parameters: data, optional options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEmpiricalModeDecomposition.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EMD-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options = struct('method','emd');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L312-L314
if ~isfield(options,'max_num_imf')
    options.max_num_imf = 10;
end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L319-L321
    if ~isfield(options,'max_num_extrema')
        options.max_num_extrema = 1;
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleEmpiricalModeDecomposition.m:L324-L326
    if ~isfield(options,'interpolation')
        options.interpolation = 'pchip';
    end
%% End copied source
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end

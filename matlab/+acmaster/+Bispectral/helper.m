function [retval,id] = helper(params,id)
% Bispectral.helper parameters: data, optional options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralDefaults.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralPlot.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Bispectral-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options = bispectralDefaults(p.data);
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r = struct('data',p.data,'options',options);
end

function [retval,id] = analyzer(params,id)
% bispectralLocalDataValidation.analyzer parameters: outputParent arguments (cell).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralLocalDataValidation.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralLocalDataValidation-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[validation] = bispectralLocalDataValidation(p.outputParent, p.arguments{:});
r = struct();
r.validation = validation;
end

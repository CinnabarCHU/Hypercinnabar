function [retval,id] = analyzer(params,id)
% bispectralValidateExamples.analyzer parameters: outputDirectory arguments (cell).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralValidateExamples.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralValidateExamples-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[validation] = bispectralValidateExamples(p.outputDirectory, p.arguments{:});
r = struct();
r.validation = validation;
end

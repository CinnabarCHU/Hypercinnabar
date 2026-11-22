function [retval,id] = analyzer(params,id)
% bispectralSelfTest.analyzer parameters: arguments (cell).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralSelfTest.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralSelfTest-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[report] = bispectralSelfTest(p.arguments{:});
r = struct();
r.report = report;
end

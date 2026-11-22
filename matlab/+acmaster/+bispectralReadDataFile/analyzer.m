function [retval,id] = analyzer(params,id)
% bispectralReadDataFile.analyzer parameters: dataPath.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralReadDataFile.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralReadDataFile-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[data, errorMessage] = bispectralReadDataFile(p.dataPath);
r = struct();
r.data = data;
r.errorMessage = errorMessage;
end

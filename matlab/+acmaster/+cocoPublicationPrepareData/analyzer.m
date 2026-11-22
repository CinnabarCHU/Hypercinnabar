function [retval,id] = analyzer(params,id)
% cocoPublicationPrepareData.analyzer parameters: rawData label.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoPublicationPrepareData.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoPublicationPrepareData-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[data, info] = cocoPublicationPrepareData(p.rawData, p.label);
r = struct();
r.data = data;
r.info = info;
end

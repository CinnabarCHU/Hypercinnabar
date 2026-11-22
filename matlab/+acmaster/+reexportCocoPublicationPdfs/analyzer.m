function [retval,id] = analyzer(params,id)
% reexportCocoPublicationPdfs.analyzer parameters: outputRoot.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/reexportCocoPublicationPdfs.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('reexportCocoPublicationPdfs-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[audit] = reexportCocoPublicationPdfs(p.outputRoot);
r = struct();
r.audit = audit;
end

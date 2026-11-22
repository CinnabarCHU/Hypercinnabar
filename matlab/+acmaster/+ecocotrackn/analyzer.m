function [retval,id] = analyzer(params,id)
% ecocotrackn.analyzer parameters: locat srsh iniloc srn method.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocotrackn.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocotrackn-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[srn1, locatnan] = ecocotrackn(p.locat, p.srsh, p.iniloc, p.srn, p.method);
r = struct();
r.srn1 = srn1;
r.locatnan = locatnan;
end

function [retval,id] = analyzer(params,id)
% eccount.analyzer parameters: srn ecc eci ecoco enorb.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/eccount.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('eccount-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[eccounts] = eccount(p.srn, p.ecc, p.eci, p.ecoco, p.enorb);
r = struct();
r.eccounts = eccounts;
end

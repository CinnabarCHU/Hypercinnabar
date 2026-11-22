function [retval,id] = analyzer(params,id)
% gammcf.analyzer parameters: a x.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/gammcf.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('gammcf-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[gammcf1, gln] = gammcf(p.a, p.x);
r = struct();
r.gammcf1 = gammcf1;
r.gln = gln;
end

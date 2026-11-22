function [retval,id] = analyzer(params,id)
% gammln.analyzer parameters: xx.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/gammln.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('gammln-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[gammln1, xx] = gammln(p.xx);
r = struct();
r.gammln1 = gammln1;
r.xx = xx;
end

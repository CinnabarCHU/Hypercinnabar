function [retval,id] = analyzer(params,id)
% gammp.analyzer parameters: a x.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/gammp.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('gammp-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result] = gammp(p.a, p.x);
r = struct();
r.result = result;
end

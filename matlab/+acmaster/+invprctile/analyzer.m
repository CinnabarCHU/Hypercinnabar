function [retval,id] = analyzer(params,id)
% invprctile.analyzer parameters: x xq dim plot_pos.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/invprctile.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('invprctile-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[p] = invprctile(p.x, p.xq, p.dim, p.plot_pos);
r = struct();
r.p = p;
end

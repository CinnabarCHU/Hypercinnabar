function [retval,id] = analyzer(params,id)
% emdNL.analyzer parameters: y goal pollFcn.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/emdNL.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('emdNL-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[c] = emdNL(p.y, p.goal, p.pollFcn);
r = struct();
r.c = c;
end

function [retval,id] = analyzer(params,id)
% datapreproc.analyzer parameters: target.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/datapreproc.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('datapreproc-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[dat] = datapreproc(p.target, 0);
r = struct();
r.dat = dat;
end

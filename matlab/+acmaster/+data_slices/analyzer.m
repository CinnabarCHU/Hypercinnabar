function [retval,id] = analyzer(params,id)
% data_slices.analyzer parameters: dat slices.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/data_slices.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('data_slices-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[datanew] = data_slices(p.dat, p.slices);
r = struct();
r.datanew = datanew;
end

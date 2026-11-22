function [retval, id] = analyzer(params, id)
% data_slices.analyzer parameters: dat slices.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/data_slices.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('data_slices-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[datanew] = data_slices(p.dat, p.slices);
r = struct();
r.datanew = datanew;
end

function [retval,id] = analyzer(params,id)
% bispectralEstimate.analyzer parameters: y dt options state.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralEstimate.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralEstimate-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[estimate, state] = bispectralEstimate(p.y, p.dt, p.options, p.state);
r = struct();
r.estimate = estimate;
r.state = state;
end

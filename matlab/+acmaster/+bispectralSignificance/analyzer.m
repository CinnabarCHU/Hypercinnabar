function [retval,id] = analyzer(params,id)
% bispectralSignificance.analyzer parameters: y dt options observed state.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralSignificance.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralSignificance-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[significance] = bispectralSignificance(p.y, p.dt, p.options, p.observed, p.state);
r = struct();
r.significance = significance;
end

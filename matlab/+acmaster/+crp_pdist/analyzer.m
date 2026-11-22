function [retval,id] = analyzer(params,id)
% crp_pdist.analyzer parameters: x w ws theiler_window lmin threshold method_use normFlag m tau.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/recurrence/crp_pdist.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('crp_pdist-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[Y, testi] = crp_pdist(p.x, p.w, p.ws, p.theiler_window, p.lmin, 0, p.threshold, p.method_use, p.normFlag, p.m, p.tau);
r = struct();
r.Y = Y;
r.testi = testi;
end

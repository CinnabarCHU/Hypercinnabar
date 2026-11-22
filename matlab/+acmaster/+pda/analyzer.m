function [retval,id] = analyzer(params,id)
% pda.analyzer parameters: data fmin fmax window nw.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/pda.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('pda-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[powratio, m] = pda(p.data, p.fmin, p.fmax, p.window, p.nw);
r = struct();
r.powratio = powratio;
r.m = m;
end

function [retval,id] = analyzer(params,id)
% redconfML.analyzer parameters: x dt nw nfft linlog smoothwin fmax fitFmax.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/redconfML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('redconfML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rhoM, s0M, redconfAR1, redconfML96] = redconfML( ...
    p.x, p.dt, p.nw, p.nfft, p.linlog, p.smoothwin, p.fmax, 0, p.fitFmax);
r = struct();
r.rhoM = rhoM;
r.s0M = s0M;
r.redconfAR1 = redconfAR1;
r.redconfML96 = redconfML96;
end

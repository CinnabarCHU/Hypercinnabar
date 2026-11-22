function [retval,id] = analyzer(params,id)
% period.analyzer parameters: x time_ml ndata avex nout xfint varx.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/period.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('period-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[x, time_ml, ndata, avex, nout, ...
    xfint, pow, freq] = period(p.x, p.time_ml, p.ndata, p.avex, p.nout, p.xfint, p.varx);
r = struct();
r.x = x;
r.time_ml = time_ml;
r.ndata = ndata;
r.avex = avex;
r.nout = nout;
r.xfint = xfint;
r.pow = pow;
r.freq = freq;
end

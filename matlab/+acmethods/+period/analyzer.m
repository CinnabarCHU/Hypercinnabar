function [retval, id] = analyzer(params, id)
% period.analyzer parameters: x time_ml ndata avex nout xfint varx.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/period.m#L6
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('period-v1.0/analyzer', params, id, @execute);
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

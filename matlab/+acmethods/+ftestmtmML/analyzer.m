function [retval, id] = analyzer(params, id)
% ftestmtmML.analyzer parameters: data NW npad.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/ftestmtmML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ftestmtmML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[freq1, ftest, fsigout, Amp, Faz, ...
    Sig, Noi, dof, wt] = ftestmtmML(p.data, p.NW, p.npad, 0);
r = struct();
r.freq1 = freq1;
r.ftest = ftest;
r.fsigout = fsigout;
r.Amp = Amp;
r.Faz = Faz;
r.Sig = Sig;
r.Noi = Noi;
r.dof = dof;
r.wt = wt;
end

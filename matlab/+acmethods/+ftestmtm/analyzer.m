function [retval, id] = analyzer(params, id)
% ftestmtm.analyzer parameters: t y NW dof npad.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/ftestmtm.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ftestmtm-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[freq, ftest, fsig, Amp, Faz, ...
    Sig, Noi] = ftestmtm(p.t, p.y, p.NW, p.dof, p.npad);
r = struct();
r.freq = freq;
r.ftest = ftest;
r.fsig = fsig;
r.Amp = Amp;
r.Faz = Faz;
r.Sig = Sig;
r.Noi = Noi;
end

function [retval,id] = analyzer(params,id)
% ftestmtm.analyzer parameters: t y NW dof npad.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/ftestmtm.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ftestmtm-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[freq, ftest, fsig, Amp, Faz, Sig, Noi] = ftestmtm(p.t, p.y, p.NW, p.dof, p.npad);
r = struct();
r.freq = freq;
r.ftest = ftest;
r.fsig = fsig;
r.Amp = Amp;
r.Faz = Faz;
r.Sig = Sig;
r.Noi = Noi;
end

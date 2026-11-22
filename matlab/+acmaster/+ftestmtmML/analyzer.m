function [retval,id] = analyzer(params,id)
% ftestmtmML.analyzer parameters: data NW npad.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/ftestmtmML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ftestmtmML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[freq1, ftest, fsigout, Amp, Faz, Sig, Noi, dof, wt] = ftestmtmML(p.data, p.NW, p.npad, 0);
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

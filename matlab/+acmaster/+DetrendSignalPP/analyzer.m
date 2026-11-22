function [retval,id] = analyzer(params,id)
% DetrendSignalPP.analyzer parameters: signal windowsize fs Porder.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/DetrendSignalPP.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DetrendSignalPP-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[signal, sigo] = DetrendSignalPP(p.signal, p.windowsize, p.fs, p.Porder);
r = struct();
r.signal = signal;
r.sigo = sigo;
end

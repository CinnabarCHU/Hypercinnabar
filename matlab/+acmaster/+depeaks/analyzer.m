function [retval,id] = analyzer(params,id)
% depeaks.analyzer parameters: data ymin_cut ymax_cut.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/depeaks.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('depeaks-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[depeaksinter] = depeaks(p.data, p.ymin_cut, p.ymax_cut);
r = struct();
r.depeaksinter = depeaksinter;
end

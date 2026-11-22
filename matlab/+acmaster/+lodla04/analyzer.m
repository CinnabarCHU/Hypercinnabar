function [retval,id] = analyzer(params,id)
% lodla04.analyzer parameters: T.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/lodla04.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('lodla04-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[lod, doy] = lodla04(p.T);
r = struct();
r.lod = lod;
r.doy = doy;
end

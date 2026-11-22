function [retval,id] = analyzer(params,id)
% redconf_any.analyzer parameters: f pxx dt smoothwin linlog.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/redconf_any.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('redconf_any-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[theored1] = redconf_any(p.f, p.pxx, p.dt, p.smoothwin, p.linlog);
r = struct();
r.theored1 = theored1;
end

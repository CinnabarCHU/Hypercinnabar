function [retval,id] = analyzer(params,id)
% mmdd2dayi.analyzer parameters: doy.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/mmdd2dayi.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('mmdd2dayi-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[mm, dd] = mmdd2dayi(p.doy);
r = struct();
r.mm = mm;
r.dd = dd;
end

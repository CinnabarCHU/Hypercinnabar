function [retval,id] = analyzer(params,id)
% monthday2dayi.analyzer parameters: month day.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/monthday2dayi.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('monthday2dayi-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[dayi] = monthday2dayi(p.month, p.day);
r = struct();
r.dayi = dayi;
end

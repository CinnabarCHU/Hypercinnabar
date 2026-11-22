function [retval, id] = analyzer(params, id)
% monthday2dayi.analyzer parameters: month day.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/monthday2dayi.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('monthday2dayi-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[dayi] = monthday2dayi(p.month, p.day);
r = struct();
r.dayi = dayi;
end

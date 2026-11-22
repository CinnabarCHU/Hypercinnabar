function [retval, id] = analyzer(params, id)
% targetadj_real.analyzer parameters: target f power orbit7 rayleigh sr.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/targetadj_real.m#L13
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('targetadj_real-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[targ] = targetadj_real(p.target, p.f, p.power, p.orbit7, p.rayleigh, p.sr);
r = struct();
r.targ = targ;
end

function [retval,id] = analyzer(params,id)
% targetadj_real.analyzer parameters: target f power orbit7 rayleigh sr.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/targetadj_real.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('targetadj_real-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[targ] = targetadj_real(p.target, p.f, p.power, p.orbit7, p.rayleigh, p.sr);
r = struct();
r.targ = targ;
end

function [retval,id] = analyzer(params,id)
% eemd.analyzer parameters: y goal ens nos.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/eemd.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('eemd-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[modes] = eemd(p.y, p.goal, p.ens, p.nos);
r = struct();
r.modes = modes;
end

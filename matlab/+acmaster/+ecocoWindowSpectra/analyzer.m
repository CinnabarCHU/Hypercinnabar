function [retval,id] = analyzer(params,id)
% ecocoWindowSpectra.analyzer parameters: values dt pad red.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoWindowSpectra.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoWindowSpectra-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[power, frequency] = ecocoWindowSpectra(p.values, p.dt, p.pad, p.red);
r = struct();
r.power = power;
r.frequency = frequency;
end

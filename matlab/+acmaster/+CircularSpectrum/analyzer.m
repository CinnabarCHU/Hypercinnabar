function [retval,id] = analyzer(params,id)
% CircularSpectrum.analyzer parameters: eventCoordinates periodMinimum periodMaximum periodCount gridMode.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleCircularSpectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('CircularSpectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleCircularSpectrum( ...
    p.eventCoordinates, p.periodMinimum, p.periodMaximum, p.periodCount, p.gridMode);
r = struct();
r.result = result;
r.meta = meta;
end

function [retval,id] = analyzer(params,id)
% dynamic_filter_lang.analyzer parameters: data window step fmin fmax unit norm padding.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/dynamic_filter_lang.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('dynamic_filter_lang-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[xdata_filtered, time, freqboundlow, freqboundhigh, cancelled] = dynamic_filter_lang( ...
    p.data, p.window, p.step, p.fmin, p.fmax, p.unit, p.norm, p.padding);
r = struct();
r.xdata_filtered = xdata_filtered;
r.time = time;
r.freqboundlow = freqboundlow;
r.freqboundhigh = freqboundhigh;
r.cancelled = cancelled;
end

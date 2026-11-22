function [retval,id] = plotter(params,id)
% Bispectral.plotter parameters: result settings (BispectralView.helper).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralPlot.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Bispectral-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
settings = p.settings;
accompat.requireFields(settings, ...
    {'Quantity','KeepStrongestFraction','BispectrumKeepStrongestFraction','PlotKeepStrongestBispectrumFraction','BicoherenceKeepStrongestFraction','PlotKeepStrongestBicoherenceFraction','ColorGrid','FrequencyMinimum','FrequencyMaximum','ReferencePeriods','FrequencyPairs','ShowPeriodAxes','PeakCount','ShowSignificance','Title','Visible'});
bispectralPlot(p.result,settings);
r = [];
end

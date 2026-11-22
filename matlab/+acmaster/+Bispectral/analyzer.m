function [retval,id] = analyzer(params,id)
% Bispectral.analyzer parameters: data options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralAnalyze.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralDefaults.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Bispectral-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options, ...
    {'InputPolicy','Estimator','NumSegments','OverlapPercent','Window','SegmentDetrendMethod','FrequencySmoothingSpan','FrequencySmoothingKernel','DetrendMethod','PolynomialOrder','Standardize','Interpolate','InterpolationMethod','SampleInterval','IrregularTolerance','GapWarningFactor','NFFT','ZeroPaddingFactor','MaxFrequencyBins','FrequencyMin','FrequencyMax','SignificanceMethod','ConfidenceLevel','NumSurrogates','SurrogateType','IAAFTIterations','IAAFTSpectralTolerance','MaxSurrogateAttempts','RandomSeed','ProgressFcn','InputName','CoordinateUnit','PlotQuantity','PlotKeepStrongestBispectrumFraction','PlotKeepStrongestBicoherenceFraction','PlotColorGrid','PlotReferencePeriods','PlotFrequencyPairs','PlotPeakCount','ShowPeriodAxes'});
r = bispectralAnalyze(p.data,p.options);
end

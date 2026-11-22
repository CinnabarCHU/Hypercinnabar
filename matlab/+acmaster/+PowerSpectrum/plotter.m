function [retval,id] = plotter(params,id)
% PowerSpectrum.plotter parameters: result fmin fmax usePeriod logFrequency.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PowerSpectrum-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
ax = axes('Parent',figure); v = p.result;
plotFrequencySeriesForMode(ax,v.frequency,v.power,p.fmin,p.fmax,p.usePeriod, ...
    'k-','LineWidth',1.2,'DisplayName','Power');
configureFrequencyAxesForMode(ax,p.fmin,p.fmax,p.usePeriod,p.logFrequency);
r = [];
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1671-L1684
        function lineHandle = plotFrequencySeriesForMode( ...
                axh,frequency,values,fmin,fmax,usePeriod,varargin)
            frequency = frequency(:);
            values = values(:);
            keepPlot = isfinite(frequency) & isfinite(values) & ...
                frequency >= fmin & frequency <= fmax;
            if usePeriod
                keepPlot = keepPlot & frequency > 0;
                xPlot = 1./frequency(keepPlot);
            else
                xPlot = frequency(keepPlot);
            end
            lineHandle = plot(axh,xPlot,values(keepPlot),varargin{:});
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1709-L1752
        function configureFrequencyAxesForMode( ...
                axesHandles,fmin,fmax,usePeriod,useLog)
            axesHandles = axesHandles(isgraphics(axesHandles));
            for axisHandle = axesHandles(:)'
                if usePeriod
                    positiveLow = fmin;
                    if ~(isfinite(positiveLow) && positiveLow > 0)
                        plottedLines = findall(axisHandle,'Type','line');
                        positivePeriods = [];
                        for lineIndex = 1:numel(plottedLines)
                            values = plottedLines(lineIndex).XData;
                            positivePeriods = [positivePeriods; ...
                                values(isfinite(values) & values > 0)']; %#ok<AGROW>
                        end
                        if isempty(positivePeriods)
                            continue
                        end
                        periodLimits = [1/fmax,max(positivePeriods)];
                    else
                        periodLimits = sort([1/fmax,1/positiveLow]);
                    end
                    if periodLimits(1) == periodLimits(2)
                        periodLimits(2) = periodLimits(1)*(1+eps);
                    end
                    xlim(axisHandle,periodLimits);
                    set(axisHandle,'XDir','reverse');
                else
                    if useLog && fmin <= 0
                        positiveFrequencies = plottedPositiveXData( ...
                            axisHandle);
                        if isempty(positiveFrequencies)
                            continue
                        end
                        xlim(axisHandle,[min(positiveFrequencies) fmax]);
                    else
                        xlim(axisHandle,[fmin fmax]);
                    end
                    set(axisHandle,'XDir','normal');
                end
                set(axisHandle,'XScale', ...
                    ternary(useLog,'log','linear'));
                set(axisHandle,'XMinorTick','on');
            end
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1754-L1761
        function values = plottedPositiveXData(axisHandle)
            values = [];
            plottedLines = findall(axisHandle,'Type','line');
            for lineIndex = 1:numel(plottedLines)
                current = plottedLines(lineIndex).XData;
                values = [values,current(isfinite(current) & current > 0)]; %#ok<AGROW>
            end
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1958-L1964
function v = ternary(tf,a,b)
if tf
    v = a;
else
    v = b;
end
end
%% End copied source

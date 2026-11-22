function [retval,id] = plotter(params,id)
% PowerSpectrum.plotter parameters: result fmin fmax usePeriod logFrequency logPower; swaSelection for SWA.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PowerSpectrum-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
v = p.result; ax = axes('Parent',figure); hold(ax,'on');
fmin=p.fmin; fmax=p.fmax; usePeriod=p.usePeriod; useLog=p.logFrequency;
plotFrequencySeries = @(axh,x,y,lo,hi,varargin) plotFrequencySeriesForMode(axh,x,y,lo,hi,usePeriod,varargin{:});
plotFrequencySeries(ax,v.frequency,v.power,fmin,fmax,'k-','LineWidth',1.2,'DisplayName','Power');
if isfield(v.models,'robust')
    robust=v.models.robust; robustSmoothingFraction=v.smoothFraction;
    if isfield(robust,'smoothed')
        redconfAR1=robust.smoothed; redconfML96=robust.levels;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L562-L570
                        rr0 = redconfAR1(:,1) >= fmin & redconfAR1(:,1) <= fmax;
                        rr = redconfML96(:,1) >= fmin & redconfML96(:,1) <= fmax;
                        plotFrequencySeries(ax,redconfAR1(rr0,1),redconfAR1(rr0,3),fmin,fmax, ...
                            'm-.','LineWidth',1.0,'DisplayName', ...
                            smoothingLegend(robustSmoothingFraction));
                        plotFrequencySeries(ax,redconfML96(rr,1),redconfML96(rr,3),fmin,fmax,'k-','LineWidth',1.8,'DisplayName','Robust AR(1)');
                        plotFrequencySeries(ax,redconfML96(rr,1),redconfML96(rr,4),fmin,fmax,'r-','LineWidth',0.9,'DisplayName','Robust 90%');
                        plotFrequencySeries(ax,redconfML96(rr,1),redconfML96(rr,5),fmin,fmax,'r--','LineWidth',1.4,'DisplayName','Robust 95%');
                        plotFrequencySeries(ax,redconfML96(rr,1),redconfML96(rr,6),fmin,fmax,'b-.','LineWidth',1.0,'DisplayName','Robust 99%');
%% End copied source
    else
        fR=robust.frequency; pth=robust.levels;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L582-L588
                        rr = fR >= fmin & fR <= fmax;
                        plotFrequencySeries(ax,fR(rr),pth(2,rr),fmin,fmax,'k-','LineWidth',1.8,'DisplayName','Robust AR(1)');
                        plotFrequencySeries(ax,fR(rr),pth(3,rr),fmin,fmax,'r-','LineWidth',0.9,'DisplayName','Robust 90%');
                        plotFrequencySeries(ax,fR(rr),pth(4,rr),fmin,fmax,'r--','LineWidth',1.4,'DisplayName','Robust 95%');
                        plotFrequencySeries(ax,fR(rr),pth(5,rr),fmin,fmax,'b-.','LineWidth',1.0,'DisplayName','Robust 99%');
                        plotFrequencySeries(ax,fR(rr),pth(1,rr),fmin,fmax,'m-.','LineWidth',1.0, ...
                            'DisplayName',smoothingLegend(robustSmoothingFraction));
%% End copied source
    end
end
if isfield(v.models,'classic')
    m=v.models.classic;
    if isstruct(m)
        fLS=m.frequency; pth=m.levels;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L639-L645
                            rr = fLS >= fmin & fLS <= fmax;
                            if any(rr)
                                fr = fLS(rr);
                                plotFrequencySeries(ax,fr,pth(1)+0*fr,fmin,fmax,'r-','LineWidth',0.9,'DisplayName','White noise 50%');
                                plotFrequencySeries(ax,fr,pth(2)+0*fr,fmin,fmax,'r--','LineWidth',1.2,'DisplayName','White noise 90%');
                                plotFrequencySeries(ax,fr,pth(3)+0*fr,fmin,fmax,'b-.','LineWidth',1.0,'DisplayName','White noise 99%');
                                plotFrequencySeries(ax,fr,pth(4)+0*fr,fmin,fmax,'g--','LineWidth',1.0,'DisplayName','White noise 99.99%');
%% End copied source
        end
    else
        fc=m(:,1); theo=m(:,3); c90=m(:,4); c95=m(:,5); c99=m(:,6); c999=m(:,7);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L602-L607
                            cc = fc >= fmin & fc <= fmax;
                            plotFrequencySeries(ax,fc(cc),theo(cc),fmin,fmax,'k-','LineWidth',1.8,'DisplayName','Classic AR(1)');
                            plotFrequencySeries(ax,fc(cc),c90(cc),fmin,fmax,'r-','LineWidth',0.9,'DisplayName','Classic 90%');
                            plotFrequencySeries(ax,fc(cc),c95(cc),fmin,fmax,'r--','LineWidth',1.4,'DisplayName','Classic 95%');
                            plotFrequencySeries(ax,fc(cc),c99(cc),fmin,fmax,'b-.','LineWidth',1.0,'DisplayName','Classic 99%');
                            plotFrequencySeries(ax,fc(cc),c999(cc),fmin,fmax,'g--','LineWidth',1.0,'DisplayName','Classic 99.9%');
%% End copied source
    end
end
for field={'powerLaw','bendingPowerLaw'}
    name=field{1};
    if isfield(v.models,name)
        q=v.models.(name); frequency=q(:,1); background=q(:,2);
        loc90=q(:,3); loc95=q(:,4); loc99=q(:,5); g90=q(:,6); g95=q(:,7); g99=q(:,8); modelName=name;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1688-L1701
            plotFrequencySeries(axh,frequency,background,fmin,fmax, ...
                'k-','LineWidth',1.6,'DisplayName',modelName);
            plotFrequencySeries(axh,frequency,loc90,fmin,fmax, ...
                'b-','LineWidth',0.8,'DisplayName','Local 90%');
            plotFrequencySeries(axh,frequency,loc95,fmin,fmax, ...
                'b--','LineWidth',1.0,'DisplayName','Local 95%');
            plotFrequencySeries(axh,frequency,loc99,fmin,fmax, ...
                'b-.','LineWidth',0.8,'DisplayName','Local 99%');
            plotFrequencySeries(axh,frequency,g90,fmin,fmax, ...
                'r-','LineWidth',0.8,'DisplayName','Global 90%');
            plotFrequencySeries(axh,frequency,g95,fmin,fmax, ...
                'r--','LineWidth',1.4,'DisplayName','Global 95%');
            plotFrequencySeries(axh,frequency,g99,fmin,fmax, ...
                'r-.','LineWidth',0.8,'DisplayName','Global 99%');
%% End copied source
    end
end
configureFrequencyAxesForMode(ax,fmin,fmax,usePeriod,useLog);
if usePeriod, axisName='Period'; else, axisName='Frequency'; end
xlabel(ax,axisName); ylabel(ax,'Power'); legend(ax,'show','Location','best');
if p.logPower, set(ax,'YScale','log'); end
if isfield(v.models,'swa')
    outSWA=v.models.swa; fx=outSWA(:,1); rr=fx>=fmin & fx<=fmax;
    swaOpts=struct('selected',p.swaSelection);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L758-L761
                            figSwa = figure('Color','white', ...
                                'Name','Acycle: SWA confidence', ...
                                'Tag','spectrumSwaFigure');
                            axSwa = axes(figSwa); hold(axSwa,'on');
%% End copied source
    plotSwaLines(axSwa,fx(rr),outSWA(rr,:),swaOpts,fmin,fmax,usePeriod);
    xlabel(axSwa,axisName); ylabel(axSwa,'Power'); set(axSwa,'YScale','log');
    configureFrequencyAxesForMode(axSwa,fmin,fmax,usePeriod,useLog); legend(axSwa,'show','Location','best');
end
if isfield(v.models,'ftest')
    q=v.models.ftest; freq=q.frequency; ftest=q.F; fsig=q.significance; Amp=q.amplitude; Faz=q.phase; dof=q.dof; nw=v.nw;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L704-L720
                        figFtest = figure('Color','white','Name', ...
                            'Acycle: F-test & Amplitude', ...
                            'Tag','spectrumFtestFigure');
                        axAmp = subplot(3,1,1,'Parent',figFtest);
                        plotFrequencySeries(axAmp,freq,Amp,fmin,fmax, ...
                            'Color',[0 0.4470 0.7410],'LineWidth',1.5);
                        ylabel(axAmp,'Amplitude');
                        title(axAmp,sprintf('Amplitude & F-test: %.6g%s', ...
                            nw,char(960)));
                        axRatio = subplot(3,1,2,'Parent',figFtest);
                        plotFrequencySeries(axRatio,freq,ftest,fmin,fmax, ...
                            'k-','LineWidth',1);
                        ylabel(axRatio,'F-ratio');
                        axSig = subplot(3,1,3,'Parent',figFtest); hold(axSig,'on');
                        fsigPlot = min(fsig,0.15);
                        plotFrequencySeries(axSig,freq,fsigPlot,fmin,fmax, ...
                            'r-','LineWidth',1);
%% End copied source
    for level=[.01 .05 .1], yline(axSig,level,'--'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L722-L725
                        ylim(axSig,[0 0.15]);
                        set(axSig,'YDir','reverse', ...
                            'YTick',[0 0.01 0.05 0.10 0.15]);
                        ylabel(axSig,'F-test significance level');
%% End copied source
    xlabel(axSig,axisName); configureFrequencyAxesForMode([axAmp axRatio axSig],fmin,fmax,usePeriod,useLog);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L729-L738
                        figFtestDiagnostics = figure('Color','white','Name', ...
                            'Acycle: F-test Diagnostics', ...
                            'Tag','spectrumFtestDiagnosticsFigure');
                        axDof = subplot(2,1,1,'Parent',figFtestDiagnostics);
                        plotFrequencySeries(axDof,freq,dof,fmin,fmax, ...
                            'k-','LineWidth',1);
                        title(axDof,'Adaptive weighted degrees of freedom');
                        axPhase = subplot(2,1,2,'Parent',figFtestDiagnostics);
                        plotFrequencySeries(axPhase,freq,Faz,fmin,fmax, ...
                            'k-','LineWidth',1);
%% End copied source
    xlabel(axPhase,axisName); configureFrequencyAxesForMode([axDof axPhase],fmin,fmax,usePeriod,useLog);
end
r=[];
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


%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1377-L1379
        function label = smoothingLegend(fraction)
            label = sprintf('%.6g%% median-smoothed',100*fraction);
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L941-L1014
        function plotSwaLines(axh,xFrequency,outRows,swaOpts, ...
                fmin,fmax,usePeriod)
            hold(axh,'on');
            pxx = outRows(:,2);
            swa = outRows(:,3);
            chi90 = outRows(:,4);
            chi95 = outRows(:,5);
            chi99 = outRows(:,6);
            chi999 = outRows(:,7);
            chi9999 = outRows(:,8);
            clfdr = outRows(:,9:13);

            for k = swaOpts.selected(:)'
                switch k
                    case 1
                        plotFrequencySeriesForMode(axh,xFrequency,swa, ...
                            fmin,fmax,usePeriod,'k-','LineWidth',1.5, ...
                            'DisplayName','SWA background');
                    case 2
                        if ~isnan(clfdr(1,1))
                            plotFrequencySeriesForMode(axh,xFrequency, ...
                                clfdr(:,1),fmin,fmax,usePeriod,'m--', ...
                                'LineWidth',0.5,'DisplayName','10% FDR');
                        end
                    case 3
                        if ~isnan(clfdr(1,2))
                            plotFrequencySeriesForMode(axh,xFrequency, ...
                                clfdr(:,2),fmin,fmax,usePeriod,'r-.', ...
                                'LineWidth',2,'DisplayName','5% FDR');
                        end
                    case 4
                        if ~isnan(clfdr(1,3))
                            plotFrequencySeriesForMode(axh,xFrequency, ...
                                clfdr(:,3),fmin,fmax,usePeriod,'b--', ...
                                'LineWidth',0.5,'DisplayName','1% FDR');
                        end
                    case 5
                        if ~isnan(clfdr(1,4))
                            plotFrequencySeriesForMode(axh,xFrequency, ...
                                clfdr(:,4),fmin,fmax,usePeriod,'g-.', ...
                                'LineWidth',0.5,'DisplayName','0.1% FDR');
                        end
                    case 6
                        if ~isnan(clfdr(1,5))
                            plotFrequencySeriesForMode(axh,xFrequency, ...
                                clfdr(:,5),fmin,fmax,usePeriod,'m-.', ...
                                'LineWidth',0.5,'DisplayName','0.01% FDR');
                        end
                    case 7
                        plotFrequencySeriesForMode(axh,xFrequency,chi90, ...
                            fmin,fmax,usePeriod,'r-','LineWidth',0.5, ...
                            'DisplayName','Chi2 90%');
                    case 8
                        plotFrequencySeriesForMode(axh,xFrequency,chi95, ...
                            fmin,fmax,usePeriod,'r--','LineWidth',2, ...
                            'DisplayName','Chi2 95%');
                    case 9
                        plotFrequencySeriesForMode(axh,xFrequency,chi99, ...
                            fmin,fmax,usePeriod,'b-.','LineWidth',0.5, ...
                            'DisplayName','Chi2 99%');
                    case 10
                        plotFrequencySeriesForMode(axh,xFrequency,chi999, ...
                            fmin,fmax,usePeriod,'m-.','LineWidth',0.5, ...
                            'DisplayName','Chi2 99.9%');
                    case 11
                        plotFrequencySeriesForMode(axh,xFrequency, ...
                            chi9999,fmin,fmax,usePeriod,'g-.', ...
                            'LineWidth',0.5,'DisplayName','Chi2 99.99%');
                end
            end

            plotFrequencySeriesForMode(axh,xFrequency,pxx,fmin,fmax, ...
                usePeriod,'k-','LineWidth',0.5,'DisplayName','Power');
        end
%% End copied source

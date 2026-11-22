function [retval,id] = plotter(params,id)
% cohac.plotter parameters: qplot F1 Cxy MSC_critical F2 phase_diff_deg phase_uncertainty_deg.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/cohac.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cohac-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
qplot = p.qplot;
F1 = p.F1;
Cxy = p.Cxy;
MSC_critical = p.MSC_critical;
F2 = p.F2;
phase_diff_deg = p.phase_diff_deg;
phase_uncertainty_deg = p.phase_uncertainty_deg;
Pangle=deg2rad(phase_diff_deg);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/cohac.m:L74-L111
if qplot > 0
    figure;
    set(gcf,'color','w');
    set(gcf,'Name','Acycle: coherence and phase');
    subplot(2,1,1)
    plot(F1,Cxy,'k','LineWidth',2)
    ylim([0 1])
    xlim([min(F1), max(F1)])
    yline(MSC_critical,'-.b');
    title('Magnitude-Squared Coherence')
    xlabel('Frequency')
    ylabel('Coherence')
    grid on;
    
    subplot(2,1,2)
    %plot(F2,phase,'r','LineWidth',2)
    errorbar(F2, phase_diff_deg, phase_uncertainty_deg);
    ylim([-180 180])
    xlim([min(F2), max(F2)])
    yline(90,'--k');
    yline(45,':k');
    yline(0,'-k');
    yline(-45,':k');
    yline(-90,'--k');
    title('Cross Spectrum Phase Difference and Uncertainty between Signals')
    xlabel('Frequency')
    ylabel(['Phase Difference (',char(176),')'])
end

if qplot > 1

    figure; 
    set(gcf,'color','w');
    set(gcf,'Name','Acycle: coherence and phase');
    polarscatter(Pangle,F2,Cxy.^2*500,'filled','MarkerFaceAlpha',.5)
    rlim([min(F2) max(F2)])
    title(['Phase lag (0-180',char(176),') and lead (180-360',char(176),')'])
end
%% End copied source
r=[];
end

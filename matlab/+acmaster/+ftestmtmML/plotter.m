function [retval,id] = plotter(params,id)
% ftestmtmML.plotter parameters: result NW fnyq.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/ftestmtmML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ftestmtmML-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
q=p.result; freq1=q.freq1; Amp=q.Amp; ftest=q.ftest; fsigout=q.fsigout; NW=p.NW; fnyq=p.fnyq;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/ftestmtmML.m:L71-L98
    figure; 
    subplot(3,1,1)
    plot(freq1, Amp,'color',[0, 0.4470, 0.7410],'LineWidth',1.5)
    xlim([0, fnyq])
    title(['Amplitude, F-test & significance level : ', num2str(NW), '\pi'])
    ylabel('Amplitude')
    
    subplot(3,1,2)
    plot(freq1, ftest,'color','k','LineWidth',1);
    xlim([0, fnyq])
    ylabel('F-ratio')
    
    subplot(3,1,3)
    fsigsh = 0.15;
    fsig1 = fsigout;
    fsig1(fsig1>fsigsh) = fsigsh;
    %yyaxis right
    plot(freq1, fsig1,'color','red','LineWidth',1);
    ylim([0.0, fsigsh])
    xlim([0, fnyq])
    line([0 fnyq],[.10 .10],'Color','k','LineWidth',0.5,'LineStyle',':')
    line([0 fnyq],[.05 .05],'Color','m','LineWidth',0.35,'LineStyle','-.')
    line([0 fnyq],[.01 .01],'Color','r','LineWidth',0.5,'LineStyle','--')
    yticks([0.0 0.01 0.05 0.10 0.15])
    yticklabels({'0','0.01', '0.05', '0.10','0.15'})
    ylabel('F-test significance level')
    xlabel('Frequency')
    set(gca, 'YDir','reverse')
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% redconfML.plotter parameters: result smoothwin.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redconfML.m#L140
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redconfML-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
a=p.result.redconfAR1; b=p.result.redconfML96; smoothwin=p.smoothwin;
ft0=a(:,1); pxx0=a(:,2); pxxsmooth0=a(:,3); ft=b(:,1); theored1=b(:,3);
chi90=b(:,4); chi95=b(:,5); chi99=b(:,6); chi999=b(:,7);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/redconfML.m:L141-L156
    figure; 
    semilogy(ft0,pxx0,'k')
    hold on; 
    semilogy(ft0,pxxsmooth0,'m-.');
    semilogy(ft,theored1,'k-','LineWidth',2);
    semilogy(ft,chi90,'r-');
    semilogy(ft,chi95,'r--','LineWidth',2);
    semilogy(ft,chi99,'b-.');
    semilogy(ft,chi999,'g--','LineWidth',1);
    xlabel('Frequency')
    ylabel('Power')
    smthwin = [num2str(smoothwin*100),'%', ' median-smoothed'];
    legend('Power',smthwin,'Robust AR(1) median',...
        'Robust AR(1) 90%','Robust AR(1) 95%','Robust AR(1) 99%','Robust AR(1) 99.9%')
    set(gcf,'units','norm') % set location
    set(gcf,'position',[0.0,0.45,0.45,0.45]) % set position
%% End copied source
r=[];
end

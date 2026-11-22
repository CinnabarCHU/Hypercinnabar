function [retval,id] = plotter(params,id)
% plomb_robustar1.plotter parameters: result smoothwin fmax.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/plomb_robustar1.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('plomb_robustar1-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
r0=p.result; f=r0.f; po=r0.po; pth=r0.pth; smoothwin=p.smoothwin; fmax=p.fmax;
pxxsmooth=pth(1,:); theored1=pth(2,:); chi90=pth(3,:); chi95=pth(4,:); chi99=pth(5,:);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/plomb_robustar1.m:L103-L119
    figure; 
    set(gcf,'Color', 'white')
    hold on; 
    %semilogy(f,chi999,'g--','LineWidth',1);
    semilogy(f,chi99,'b-.');
    semilogy(f,chi95,'r--','LineWidth',2);
    semilogy(f,chi90,'r-');
    semilogy(f,theored1,'k-','LineWidth',2);
    semilogy(f,pxxsmooth,'m-.');
    semilogy(f,po,'k')
    xlim([0,fmax])
    xlabel('Frequency')
    ylabel('Power')
    smthwin = [num2str(smoothwin*100),'%', ' median-smoothed'];
    legend( 'Robust AR(1) 99%', 'Robust AR(1) 95%','Robust AR(1) 90%',...
        'Robust AR(1) median',smthwin,'Power')
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
r=[];
end

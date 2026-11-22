function [retval, id] = plotter(params, id)
% BootstrapSmooth.plotter parameters: x y result method span.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/smoothciML.m#L44
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('BootstrapSmooth-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
X=p.x; Y=p.y; meanboot=p.result.meanboot; bootstd=p.result.bootstd; bootprt=p.result.bootprt;
method = p.method;
span = p.span;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/smoothciML.m:L44-L76
colorcode = [67/255,180/255,100/255];

figure;
set(gcf,'units','norm') % set location
set(gcf,'position',[0.005,0.45,0.38,0.45]) % set position
set(gcf,'color','w');
hold on
fill([X', fliplr(X')],[(meanboot + 2 * bootstd)', fliplr((meanboot - 2 * bootstd)')],colorcode,'LineStyle','none','facealpha',.2)
fill([X', fliplr(X')],[(meanboot + bootstd)', fliplr((meanboot - bootstd)')],colorcode,'LineStyle','none','facealpha',.6)
plot(X,meanboot,'Color',[0,120/255,0],'LineWidth',1.5,'LineStyle','-')
scatter(X,Y,'b')
title([num2str(span*100),' % ',method,' regression'])
legend('2\sigma confidence intervals','1\sigma confidence intervals',...
    'mean','Data',...
    'Location','NorthEast','Interpreter','tex');
hold off

figure;
set(gcf,'units','norm') % set location
set(gcf,'position',[0.385,0.45,0.38,0.45]) % set position
set(gcf,'color','w');
hold on
fill([X', fliplr(X')],[(bootprt(:,end))', fliplr((bootprt(:,1))')],colorcode,'LineStyle','none','facealpha',.1)
fill([X', fliplr(X')],[(bootprt(:,end-1))', fliplr((bootprt(:,2))')],colorcode,'LineStyle','none','facealpha',.3)
fill([X', fliplr(X')],[(bootprt(:,end-2))', fliplr((bootprt(:,3))')],colorcode,'LineStyle','none','facealpha',.5)
fill([X', fliplr(X')],[(bootprt(:,end-3))', fliplr((bootprt(:,4))')],colorcode,'LineStyle','none','facealpha',.9)
plot(X,bootprt(:,5),'Color',[0,120/255,0],'LineWidth',1.5,'LineStyle','-')
scatter(X,Y,'b')
title([num2str(span*100),' % ',method,' regression'])
legend('99% confidence intervals','95% confidence intervals','90% confidence intervals',...
    '50% confidence intervals','median','Data',...
    'Location','NorthEast');
hold off
%% End copied source
r=[];
end

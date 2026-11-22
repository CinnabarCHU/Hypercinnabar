function [retval, id] = plotter(params, id)
% StratigraphicCorrelation.plotter parameters: reference data1 tiepoints1 tiepoints2 refxmin refxmax serxmin serxmax result.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/CorrelationGUI.m#L273
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/CorrelationGUI.m#L441
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('StratigraphicCorrelation-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
refxmin = p.refxmin;
refxmax = p.refxmax;
serxmin = p.serxmin;
serxmax = p.serxmax;
tiepoints1 = p.tiepoints1;
tiepoints2 = p.tiepoints2;
rawref=p.reference; rawser=p.data1; q=p.result;
data1t=q.data1t; time1=data1t(:,1); tie2t=q.tie2t; tiepoints2sort=sortrows(tiepoints2);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L273-L276
    CorrFig = figure;
    set(CorrFig,'units','norm') % set units as normalized
    set(CorrFig,'position',[0.01,0.3,0.9,0.65]) % set position
    set(CorrFig,'Color','white')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L278-L278
        set(CorrFig,'Name','Acycle: Stratigraphic Correlation')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L282-L284
    subplot(3,1,1)
    plot(rawref(:,1),rawref(:,2),'-','color',[128 128 128]/255)
    xlim([refxmin, refxmax])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L286-L287
        xlabel('Time')
        ylabel('Value')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L290-L290
        legend('Reference')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L298-L301
    xl = xlim;
    yl = ylim;
    tieshiftx = (xl(2)-xl(1));
    tieshifty = (yl(2)-yl(1));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L303-L305
    subplot(3,1,2)
    plot(rawser(:,1),rawser(:,2),'b-')
    xlim([serxmin, serxmax])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L307-L309
        xlabel('Depth')
        ylabel('Value')
        title('\fontsize{14}\color{blue}Series')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L315-L318
    xl2 = xlim;
    yl2 = ylim;
    tieshiftx2 = (xl2(2)-xl2(1));
    tieshifty2 = (yl2(2)-yl2(1));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L333-L333
shiftv = 0.005;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L368-L374
        subplot(3,1,1)
        plot(rawref(:,1),rawref(:,2),'-','color',[128 128 128]/255)
        xlim([refxmin, refxmax])
        hold on
        plot(tiepoints1(:,1),tiepoints1(:,2),'*','color',[128 0 0]/255)
        text(tiepoints1(:,1)+shiftv*tieshiftx,tiepoints1(:,2)+shiftv*tieshifty,num2str(tiepoints1(:,3)))
        hold off
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L403-L409
            subplot(3,1,2)
            plot(rawser(:,1),rawser(:,2),'b-')
            xlim([serxmin, serxmax])
            hold on
            plot(tiepoints2(:,1),tiepoints2(:,2),'r*')
            text(tiepoints2(:,1)+shiftv*tieshiftx2,tiepoints2(:,2)+shiftv*tieshifty2,num2str(tiepoints2(:,3)))
            hold off
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L441-L454
            subplot(3,1,3)
            plot(rawref(:,1),(rawref(:,2)-mean(rawref(:,2)))/std(rawref(:,2)),'-','color',[128 128 128]/255)
            hold on
            plot(tiepoints1(:,1),(tiepoints1(:,2)-mean(rawref(:,2)))/std(rawref(:,2)),'*','color',[128 0 0]/255)
            text(tiepoints1(:,1)+shiftv*tieshiftx,...
                (tiepoints1(:,2)-mean(rawref(:,2)))/std(rawref(:,2))+0.2,num2str(tiepoints1(:,3)))
            
            plot(time1,(data1t(:,2)- mean(data1t(:,2)))/std(data1t(:,2)),'b-')
            plot(tie2t,(tiepoints2sort(:,2)-mean(rawser(:,2)))/std(rawser(:,2)),'r*')
            %text(tie2t+shiftv*tieshiftx,...
            %    (tiepoints2sort(:,2)-mean(rawser(:,2)))/std(rawser(:,2))+0.2,num2str(tiepoints2sort(:,3)))
            
            xlim([min(refxmin,min(time1)), max(refxmax,max(time1))])
            hold off
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L456-L458
                xlabel('Time')
                ylabel('Standardized Value')
                title('Reference vs. Tuned Series')
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% rmse4leadlag.plotter parameters: result target series timedir.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/leadlagGUI.m#L208
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/rmse4leadlag.m#L116
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rmse4leadlag-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
target = p.target;
series = p.series;
timedir = p.timedir;
llgrid=p.result.llgrid; RMSE=p.result.RMSE;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/rmse4leadlag.m:L43-L51
% start and end of the 1st column of the target
tar1 = min(target(:,1));
tar2 = max(target(:,1));
% start and end of the 1st column of the series
ser1 = min(series(:,1));
ser2 = max(series(:,1));
% common interval
sel1 = max(ser1, tar1); % lower bound
sel2 = min(ser2, tar2); % upper bound
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/rmse4leadlag.m:L62-L67
% Step 1. Select the common interval for both target and series
[series1] = select_interval(series,sel1,sel2);
[target1] = select_interval(target,sel1,sel2);
% standardized
series1(:,2) = (series1(:,2) - mean(series1(:,2)))/std(series1(:,2));
target1(:,2) = (target1(:,2) - mean(target1(:,2)))/std(target1(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/rmse4leadlag.m:L98-L114
llgridj = llgrid(RMSE==min(RMSE));

if llgridj > 0
    if timedir == 1
        leadlagid = 'lags behind';
    else
        leadlagid = 'leads';
    end
elseif llgridj == 0
    leadlagid = 'is in-phase with';
else
    if timedir == 1
        leadlagid = 'leads';
    else
        leadlagid = 'lags behind';
    end
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/rmse4leadlag.m:L117-L159
    figure;
    set(gcf,'color','white')
    plot(llgrid,RMSE,'k');
    hold on
    ylimhere = ylim;
    plot([llgridj llgridj],[ylimhere(1) ylimhere(2)],'r-.')
    if timedir == 1
        xlabel('lead (-) / lag (+)')
    else
        xlabel('lag (-) / lead (+)')
    end
    ylabel('RMSE')
    title(['Min RMSE @ ', num2str(llgridj),'. Target ',leadlagid,' reference.'])
    
    figure;
    set(gcf,'color','white')
    subplot(311)
    plot(target(:,1),target(:,2),'b-')
    xlim([min(target(:,1)),max(target(:,1))]);
    title('Reference')
    subplot(312)
    plot(series(:,1),series(:,2),'k-')
    if llgridj ~=0
        hold on
        plot(series(:,1)+llgridj, series(:,2),'r-.')
        legend({'Raw target';'Adjusted target'});
    end
    xlim([min(target(:,1)),max(target(:,1))]);
    title('Target')
    
    subplot(313)
    plot(target1(:,1),target1(:,2),'b-')
    hold on;
    plot(series1(:,1),series1(:,2),'k-')
    
    if llgridj ~=0
        plot(series1(:,1)+llgridj, series1(:,2),'r-.')
        %legend({'Target';'Raw series';'Adjusted series'})
    end
    xlim([min(target1(:,1)),max(target1(:,1))]);
    hold off;
    xlabel('Depth/Time')
    ylabel('Standardized value')
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% AgeScale.plotter parameters: data tiepoints result view unit filename.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L320
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L389
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L433
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L607
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AgeScale-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data=p.data; tiepoints=p.tiepoints; time=p.result.time;
dat_name=p.filename; handles=struct('unit',p.unit,'lang_choice',0);
switch p.view
    case 'series'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L335-L339
figdata = figure;
xmax1 = nan;
xmin1 = nan;
xmax2 = nan;
xmin2 = nan;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L345-L349
    subplot(2,1,1)
    plot(data(:,1),data(:,2)); hold on;
    set(gca,'XMinorTick','on','YMinorTick','on')
    xmin1 = nanmin(xmin1,min(data(:,1)));
    xmax1 = nanmax(xmax1,max(data(:,1)));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L351-L351
        title('Origin data')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L357-L357
    xlim([xmin1,xmax1])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L360-L362
    subplot(2,1,2)
    plot(time,data(:,2)); hold on;
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L364-L364
        title('Tuned data')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L370-L372
    xmin2 = nanmin(xmin2,min(time));
    xmax2 = nanmax(xmax2,max(time));
    xlim([xmin2,xmax2])
%% End copied source
    case 'model'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L398-L412
x1 = min(tiepoints(:,1));  % depth
x2 = max(tiepoints(:,1));  % depth
y1 = min(tiepoints(:,2));  % time
y2 = max(tiepoints(:,2));  % time

figure('Position',[100 800 500 500],...
  'Color',[1 1 1])
axes('Position',[0.2 0.2 0.7 0.7],...
  'XLim',[y1 y2],...
  'YLim',[x1 x2],...
  'YDir','Reverse',...
  'Box','On',...
  'FontSize',14)
line(tiepoints(:,2),tiepoints(:,1),...
  'LineWidth',1)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L415-L417
    xlabel('Age')
    ylabel(['Depth (',handles.unit,')'])
    title(['Age Model'])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L428-L428
set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
    case 'age-axis'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L449-L601
    t1 = min(time);  % time
    t2 = max(time);  % time
    y1 = min(data(:,2));  % value
    y2 = max(data(:,2));  % value
    d1 = min(data(:,1));  % value
    d2 = max(data(:,1));  % value
    
    t = time; 
    rec = data(:,2);

    lenexp = fix(log10(t2-t1));  % exp
    if lenexp >= 0 % length [1 10]
        XTickStep = 0.05 * round(fix((t2-t1)/10^lenexp)) * 10^lenexp;
        t1r = round(fix(t1/10^lenexp)) * 10^lenexp;
        age = t1r:XTickStep:t2;
        depthint = interp1(tiepoints(:,2),tiepoints(:,1),age,'linear','extrap');
        depthintlabels = num2str(depthint,'%.0f\n');
    else
        XTickStep = (t2-t1)/20;
        age = t1:XTickStep:t2;
        depthint = interp1(tiepoints(:,2),tiepoints(:,1),age,'linear','extrap');
        depthintlabels = num2str(depthint,'%.3f\n');
    end
    
    %  display in a first diagram with two axes.
    figure1 = figure('Position',[50 50 1000 400], 'Color',[1 1 1]) ;
    
    ax(1) = axes('Position',[0.1 0.4 0.8 0.4],...
      'Color','None',...
      'XTick',age,...
      'XLim',[t1 t2],...
      'YLim',[y1 y2],...
      'FontSize',14);
    line1 = line(t,rec,...
      'LineWidth',1);
    
    
    set(gca,'XMinorTick','on','YMinorTick','on')
    
    if handles.lang_choice==0
        xlabel(ax(1),'Age')
        ylabel(ax(1),'Proxy Value')
        title(ax(1),[dat_name,': Tuned'], 'Interpreter', 'none')
    else
        [~, locb1] = ismember('main22',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(1),lang_var{locb1})
        [~, locb1] = ismember('main24',handles.lang_id);
        ylabel(ax(1),lang_var{locb1})
        [~, locb1] = ismember('a42',handles.lang_id);
        title(ax(1),[dat_name,': ',lang_var{locb1}], 'Interpreter', 'none')
    end

    ax(2) = axes('Position',[0.1 0.25 0.8 0.4],...
      'Color','None',...
      'XLim',[t1 t2],...
      'XTickMode','Manual',...
      'XTick',age,...
      'XTickLabels',depthintlabels,...
      'YLim',[y1 y2],...
      'YTick',[],...
      'YColor','None',...
      'FontSize',14);
    if handles.lang_choice==0
        xlabel(ax(2),['Depth (',handles.unit,')'])
    else
        [~, locb] = ismember('main23',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(2),[lang_var{locb},' (',handles.unit,')'])
    end
    set(gca,'XMinorTick','on','YMinorTick','on')
    
    % Then we interpolate the  ages to an evenly-spaced depth scale
    
    lenexp = fix(log10(d2-d1));  % exp
    if lenexp >= 0 % length [1 10]
        XTickStep = 0.05 * round(fix((d2-d1)/10^lenexp)) * 10^lenexp;
        if d1>=0
            d1r = round(fix(d1/10^lenexp)) * 10^lenexp;
        else
            d1r = round(d1);
        end
        depth = d1r:XTickStep:d2;
        ageint = interp1(depthint,age,depth,'linear','extrap');
        depthlabels = num2str(depth,'%.0f\n');
    else
        XTickStep = (d2-d1)/20;
        depth = d1:XTickStep:d2;
        ageint = interp1(depthint,age,depth,'linear','extrap');
        depthlabels = num2str(depth,'%.3f\n');
    end

    figure1 = figure('Position',[50 500 1000 400],...
      'Color',[1 1 1]);
    ax(1) = axes('Position',[0.1 0.4 0.8 0.4],...
      'Color','None',...
      'XLim',[t1 t2],...
      'XTick',age,...
      'YLim',[y1 y2],...
      'FontSize',14);
    line1 = line(t,rec,...
      'LineWidth',1);
    
    if handles.lang_choice==0
        xlabel(ax(1),'Age')
        ylabel(ax(1),'Proxy Value')
        title(ax(1),[dat_name,': Tuned'], 'Interpreter', 'none')
    else
        [~, locb1] = ismember('main22',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(1),lang_var{locb1})
        [~, locb1] = ismember('main24',handles.lang_id);
        ylabel(ax(1),lang_var{locb1})
        [~, locb1] = ismember('a42',handles.lang_id);
        title(ax(1),[dat_name,': ',lang_var{locb1}], 'Interpreter', 'none')
    end
    
    set(gca,'XMinorTick','on','YMinorTick','on')
    try
        ax(2) = axes('Position',[0.1 0.25 0.8 0.4],...
          'Color','None',...
          'XLim',[t1 t2],...
          'XTickMode','Manual',...
          'XTick',ageint,...
          'XTickLabels',depthlabels,...
          'YLim',[y1 y2],...
          'YTick',[],...
          'YColor','None',...
          'FontSize',14);
    catch
        ageint = fliplr(ageint);
        depth = d2:-1*XTickStep:d1r;
        depthlabels = num2str(depth,'%.0f\n');
        ax(2) = axes('Position',[0.1 0.25 0.8 0.4],...
          'Color','None',...
          'XLim',[t1 t2],...
          'XTickMode','Manual',...
          'XTick',ageint,...
          'XTickLabels',depthlabels,...
          'YLim',[y1 y2],...
          'YTick',[],...
          'YColor','None',...
          'FontSize',14);
    end
    if handles.lang_choice==0
        xlabel(ax(2),['Depth (',handles.unit,')'])
    else
        [~, locb] = ismember('main23',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(2),[lang_var{locb},' (',handles.unit,')'])
    end
    
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
    case 'depth-axis'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L623-L765
    t1 = min(time);  % time
    t2 = max(time);  % time
    y1 = min(data(:,2));  % value
    y2 = max(data(:,2));  % value
    d1 = min(data(:,1));  % value
    d2 = max(data(:,1));  % value
    
    t = time;
    rec = data(:,2);
    
    lenexp = fix(log10(d2-d1));  % exp
    if lenexp >= 0 % length [1 10]
        XTickStep = 0.1 * round(fix((d2-d1)/10^lenexp)) * 10^lenexp;
        if d1>=0
            d1r = round(fix(d1/10^lenexp)) * 10^lenexp;
        else
            d1r = round(d1);
        end
        XTickListDepth = d1r:XTickStep:d2;
        timeint = interp1(tiepoints(:,1),tiepoints(:,2),XTickListDepth,'linear','extrap');
        timeintlabels = num2str(timeint,'%.0f\n');
    else
        XTickStep = (d2-d1)/20;
        XTickListDepth = d1:XTickStep:d2;
        timeint = interp1(tiepoints(:,1),tiepoints(:,2),XTickListDepth,'linear','extrap');
        timeintlabels = num2str(timeint,'%3.3f\n');
    end
    figure1 = figure('Position',[50 50 1000 400], 'Color',[1 1 1]) ;
    ax(1) = axes('Position',[0.1 0.4 0.8 0.4],...
      'Color','None',...
      'XTick',XTickListDepth,...
      'XLim',[d1 d2],...
      'YLim',[y1 y2],...
      'FontSize',14);
    line1 = line(data(:,1),rec,...
      'LineWidth',1);
    if handles.lang_choice==0
        xlabel(ax(1),['Depth (',handles.unit,')'])
        ylabel(ax(1),'Proxy Value')
        title(ax(1),[dat_name,': Depth'], 'Interpreter', 'none')
    else
        [~, locb1] = ismember('main23',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(1),[lang_var{locb1},' (',handles.unit,')'])
        title(ax(1),[dat_name,': ',lang_var{locb1}], 'Interpreter', 'none')
        [~, locb1] = ismember('main24',handles.lang_id);
        ylabel(ax(1),lang_var{locb1})
    end
    
    set(gca,'XMinorTick','on','YMinorTick','on')
    ax(2) = axes('Position',[0.1 0.25 0.8 0.4],...
      'Color','None',...
      'XLim',[d1 d2],...
      'XTickMode','Manual',...
      'XTick',XTickListDepth,...
      'XTickLabels',timeintlabels,...
      'YLim',[y1 y2],...
      'YTick',[],...
      'YColor','None',...
      'FontSize',14);
    if handles.lang_choice==0
        xlabel(ax(2),'Age')
    else
        [~, locb] = ismember('main22',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(2),lang_var{locb})
    end
    
    set(gca,'XMinorTick','on','YMinorTick','on')
    
    % Then we interpolate the  ages to an evenly-spaced depth scale
    lenexp = fix(log10(t2-t1));  % exp
    if lenexp >= 0 % length [1 10]
        XTickStep = 0.05 * round(fix((t2-t1)/10^lenexp)) * 10^lenexp;
        t1r = round(fix(t1/10^lenexp)) * 10^lenexp;
        age = t1r:XTickStep:t2;
        depthint = interp1(tiepoints(:,2),tiepoints(:,1),age,'linear','extrap');
        depthintlabels = num2str(age,'%.0f\n');
    else
        XTickStep = (t2-t1)/20;
        age = t1:XTickStep:t2;
        depthint = interp1(tiepoints(:,2),tiepoints(:,1),age,'linear','extrap');
        depthintlabels = num2str(age,'%.3f\n');
    end

    figure1 = figure('Position',[50 500 1000 400],'Color',[1 1 1]);
    ax(1) = axes('Position',[0.1 0.4 0.8 0.4],...
      'Color','None',...
      'XTick',XTickListDepth,...
      'XLim',[d1 d2],...
      'YLim',[y1 y2],...
      'FontSize',14);
    line1 = line(data(:,1),rec,...
      'LineWidth',1);
  
    if handles.lang_choice==0
        xlabel(ax(1),['Depth (',handles.unit,')'])
        ylabel(ax(1),'Proxy Value')
        title(ax(1),[dat_name,': Depth'], 'Interpreter', 'none')
    else
        [~, locb1] = ismember('main23',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(1),[lang_var{locb1},' (',handles.unit,')'])
        title(ax(1),[dat_name,': ',lang_var{locb1}], 'Interpreter', 'none')
        [~, locb1] = ismember('main24',handles.lang_id);
        ylabel(ax(1),lang_var{locb1})
    end
    
    set(gca,'XMinorTick','on','YMinorTick','on')
    try
        ax(2) = axes('Position',[0.1 0.25 0.8 0.4],...
          'Color','None',...
          'XLim',[d1 d2],...
          'XTickMode','Manual',...
          'XTick',depthint,...
          'XTickLabels',depthintlabels,...
          'YLim',[y1 y2],...
          'YTick',[],...
          'YColor','None',...
          'FontSize',14);
    catch
        depthint = fliplr(depthint);
        age = t2:-1*XTickStep:t1r;
        depthintlabels = num2str(age,'%.3f\n');
        ax(2) = axes('Position',[0.1 0.25 0.8 0.4],...
          'Color','None',...
          'XLim',[d1 d2],...
          'XTickMode','Manual',...
          'XTick',depthint,...
          'XTickLabels',depthintlabels,...
          'YLim',[y1 y2],...
          'YTick',[],...
          'YColor','None',...
          'FontSize',14);
    end
    if handles.lang_choice==0
        xlabel(ax(2),'Age')
    else
        [~, locb] = ismember('main22',handles.lang_id);
        lang_var = handles.lang_var;
        xlabel(ax(2),lang_var{locb})
    end
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
    otherwise
        error('Acycle:AgeScale:View','Unknown age-scale figure %s.',p.view);
end
r=[];
end

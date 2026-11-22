function [retval, id] = plotter(params, id)
% PlotAdv.plotter parameters: series settings.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/plotpro_plot_done.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PlotAdv-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
series = p.series;
settings = p.settings;
handles=settings; handles.nplot=numel(series);
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/plotpro_plot_done.m:L3-L8
matrix_set = handles.matrix_set;
axis_setting = handles.axis_setting;
flipxy = handles.flipxy;
%plotprofig = figure;
hold on
for i = 1: handles.nplot
%% End copied source
dat=series{i};
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/plotpro_plot_done.m:L17-L131
        dat = dat(~any(isnan(dat),2),:);
        linestyle_list = handles.pop_linestyle_list;
        markerstyle_list = handles.pop_markerstyle_list;
% settings for x-axis 1st row and y-axis 2nd row
% 1st column = start; 2nd = end; 3nd = linear1/log0; 4th = set x or y
% %          1  2  3  4  5  6  7  8
%axis_set = {0, 0, 1, 1, 0, 0, 1, 0};
        if matrix_set{i,1} == 2
            pp = stairs(dat(:,1),dat(:,2));  % stairs plot
        elseif matrix_set{i,1} == 1
            pp = plot(dat(:,1),dat(:,2));  % line plot
        elseif matrix_set{i,1} == 4
            pp = stem(dat(:,1),dat(:,2));  % stem plot
        end
        if ismember(matrix_set{i,1}, [1, 2, 4])
            %pp.LineStyle = linestyle_list{matrix_set{i,2}};
            pp.LineWidth = matrix_set{i,3};
            pp.Color = matrix_set{i,4};
            pp.Marker = markerstyle_list{matrix_set{i,5}};
            pp.MarkerSize = matrix_set{i,6};
            if matrix_set{i,8} == 1
                pp.MarkerFaceColor = matrix_set{i,7};
            else
                pp.MarkerEdgeColor = 'none';
            end
            if matrix_set{i,10} == 1
                pp.MarkerEdgeColor = matrix_set{i,9};
            else
                pp.MarkerEdgeColor = 'none';
            end
        end
        if matrix_set{i,1} == 3
            if handles.basevalue_check == 0
                pp = bar(dat(:,1),dat(:,2));  % bar plot
            else
                pp = bar(dat(:,1),dat(:,2),handles.basevalue);  % bar plot
            end
            %pp.LineStyle = linestyle_list{matrix_set{i,2}};
            pp.LineWidth = matrix_set{i,3};
%            pp.Color = matrix_set{i,4};
%            pp.width = matrix_set{i,6};

            if matrix_set{i,8} == 1
                pp.FaceColor = matrix_set{i,7};
            else
                pp.FaceColor = 'none';
            end
            if matrix_set{i,10} == 1
                pp.EdgeColor = matrix_set{i,9};
            else
                pp.EdgeColor = 'none';
            end
        end
        if matrix_set{i,1} == 5
            if handles.basevalue_check == 0
                pp = area(dat(:,1),dat(:,2));  % area plot
            elseif handles.basevalue_check == 1
                pp = area(dat(:,1),dat(:,2),handles.basevalue);  % area plot
            end
            pp.FaceColor = matrix_set{i,4};
            %pp.LineStyle = linestyle_list{matrix_set{i,2}};
        end
        pp.LineStyle = linestyle_list{matrix_set{i,2}};
end
if axis_setting{1,1} < axis_setting{1,2}
    xlim([axis_setting{1,1} axis_setting{1,2}])
end
if axis_setting{1,5} < axis_setting{1,6}
    ylim([axis_setting{1,5} axis_setting{1,6}])
end
%xlabel(handles.unit)
xlabel(handles.xlabel)
%ylabel('Value')
ylabel(handles.ylabel)
title(handles.title)

%  settings for x-axis 1st row and y-axis 2nd row
%  1 column = start; 2 = end; 3 = linear(=1)/log(=0); 4 = set x or y
%  5 column = start; 6 = end; 7 = linear(=1)/log(=0); 8 = set x or y
%            1  2  3  4  5  6  7  8
%axis_set = {0, 0, 1, 1, 0, 0, 1, 0};

if axis_setting{1,3} == 0
    set(gca,'XScale','log')
elseif axis_setting{1,3} == 1
    set(gca,'XScale','linear')
end

if axis_setting{1,7} == 0
    set(gca,'YScale','log')
elseif axis_setting{1,7} == 1
    set(gca,'YScale','linear')
end

if flipxy(1) == 1
    set(gca,'Xdir','reverse')
else
    set(gca,'Xdir','normal')
end
if flipxy(2) == 1
    set(gca,'Ydir','reverse')
else
    set(gca,'Ydir','normal')
end

if handles.swapxy == 1
    view([90 -90])
else
    view([0 90]);
end
set(gca,'XMinorTick','on','YMinorTick','on')
%handles.plotprofig = plotprofig;
set(gcf,'color','w');
legend(handles.plot_list)
hold off
%% End copied source
r=[];
end

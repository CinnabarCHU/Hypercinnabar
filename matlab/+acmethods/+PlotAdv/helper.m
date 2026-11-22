function [retval, id] = helper(params, id)
% PlotAdv.helper parameters: series plot_list xlabel ylabel title.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/PlotAdv.m#L176
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/PlotAdv.fig
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PlotAdv-v1.0/helper', params, id, @execute);
end

function r = execute(p)
series = p.series;
plot_list = p.plot_list;
xlabel = p.xlabel;
ylabel = p.ylabel;
title = p.title;
handles.nplot=numel(series);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/PlotAdv.m:L176-L218
handles.swapxy = 0; 
colordef = [0 0 0]; % default color for the first line
colordef_list = [1 0 0; 0 0 1; 0 1 0; 0 1 1; 1 0 1; 1 1 0]; 
% default color styles for the first 2-7 lines

% Settings for plot: 
%   1 = line plots, 
%   2 = line style, 
%   3 = line size, 
%   4 = line color
%   5 = marker style, 
%   6 = marker size, 
%   7 = marker fill color, 
%   8 = maker show?, 
%   9 = marker edge color, 
%   10 = marker edge show?
%                 1  2   3      4      5   6      7      8     9      10
matrix_setting = {1, 1, 1.0, colordef, 1, 6.0, colordef, 1, colordef, 0};
matrix_set = repmat(matrix_setting,handles.nplot,1);

if handles.nplot > 1
    for i = 2 : handles.nplot
        if i < 8
            matrix_set{i,4} = colordef_list(i-1,:);
            matrix_set{i,7} = colordef_list(i-1,:);
            matrix_set{i,9} = colordef_list(i-1,:);
        else 
            matrix_set{i,4} = rand(1,3);
            matrix_set{i,7} = matrix_set{i,4};
            matrix_set{i,9} = matrix_set{i,4};
        end
    end
end

handles.matrix_set = matrix_set;

% settings for x-axis 1st row and y-axis 2nd row
% 1 column = start; 2 = end; 3 = linear(=1)/log(=0); 4 = set x or y
% 5 column = start; 6 = end; 7 = linear(=1)/log(=0); 8 = set x or y
%           1  2  3  4  5  6  7  8
axis_set = {0, 0, 1, 1, 0, 0, 1, 0};
axis_setting = repmat(axis_set,1,1);
handles.flipxy = [0, 0];   % flip axis 0 = no; 1 = yes; 1st = x; 2nd = y;
%% End copied source
for i=1:handles.nplot
    dat=series{i};
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/PlotAdv.m:L248-L260
    dat = dat(~any(isnan(dat),2),:);
    if i == 1
        axis_setting{1,1} = min(dat(:,1));
        axis_setting{1,2} = max(dat(:,1));
        axis_setting{1,5} = min(dat(:,2));
        axis_setting{1,6} = max(dat(:,2));
    end
    % update plot value
    axis_setting{1,1} = min(min(dat(:,1)), axis_setting{1,1});
    axis_setting{1,2} = max(max(dat(:,1)), axis_setting{1,2});
    axis_setting{1,5} = min(min(dat(:,2)), axis_setting{1,5});
    axis_setting{1,6} = max(max(dat(:,2)), axis_setting{1,6});
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/PlotAdv.m:L275-L276
handles.basevalue = axis_setting{1,5}; %
handles.basevalue_check = 0;
%% End copied source
handles.plot_list=plot_list; handles.xlabel=xlabel; handles.ylabel=ylabel; handles.title=title;
handles.axis_setting=axis_setting;
handles.pop_linestyle_list={'-','--',':','-.','none'};
handles.pop_markerstyle_list={'none','.','o','+','*','x','Square','Diamond','^','v','>','<','Pentagram','Hexagram'};
r=struct();
r.settings=handles;
r.series=series;
end

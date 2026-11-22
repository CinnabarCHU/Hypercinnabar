function [retval,id] = plotter(params,id)
% LinearRegression.plotter parameters: result.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/BivLinearRegUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('LinearRegression-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
x = p.result.x; y = p.result.y; yfit = p.result.fitted; stats = p.result.stats;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/BivLinearRegUI.m:L46-L74
sf = findobj(allchild(groot), 'flat', 'Name', 'Acycle: Linear Regression');
if isempty(sf)
    sf = uifigure('Name', 'Acycle: Linear Regression', ...
        'Position', [100, 100, 760, 420], ...
        'NumberTitle', 'off', 'MenuBar', 'none');
else
    delete(sf);
    sf = uifigure('Name', 'Acycle: Linear Regression', ...
        'Position', [100, 100, 760, 420], ...
        'NumberTitle', 'off', 'MenuBar', 'none');
end

uit = uitable(sf, 'Data', stats, ...
    'Units', 'normalized', ...
    'FontSize', 12, ...
    'Position', [0.03, 0.08, 0.36, 0.84], ...
    'ColumnName', {'Statistic', 'Value'}, ...
    'ColumnWidth', {130,120});

ax = uiaxes(sf, 'Units', 'normalized', 'Position', [0.45, 0.12, 0.52, 0.8]);
scatter(ax,x,y,24,'filled');
hold(ax,'on');
[xs,idx] = sort(x);
plot(ax,xs,yfit(idx),'r-','LineWidth',1.5);
hold(ax,'off');
xlabel(ax,'Column 1');
ylabel(ax,'Column 2');
title(ax,'Linear regression');
grid(ax,'on');
%% End copied source
r = [];
end

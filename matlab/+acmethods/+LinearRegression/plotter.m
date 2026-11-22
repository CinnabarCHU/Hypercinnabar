function [retval, id] = plotter(params, id)
% LinearRegression.plotter parameters: result.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8941
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LinearRegression-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
q=p.result; X=q.X; Y=q.Y; Xnew=q.Xnew; Ypred=q.Ypred; CI=q.CI; display_text=q.display_text;
%% Copied from Acycle-MATLAB-distribution@54720f36678812cca5e6286efaf91433b37047589dd2ee994049ea5020ca35dc Acycle_3.1.1/code/test/BivLinearRegUI.m:L132-L162
    figName = 'Acycle: Regression Analysis Plot';
    figlm = findobj('Type', 'figure', 'Name', figName);
    
    if isempty(figlm)
        figlm = figure('Name', figName,'Color', 'white');  % Adjust position and size as needed
    else
        figlm = figlm(1);
        clf(figlm); % Clear the figure
    end
    % Create axes
    ax = axes('Parent', figlm, 'Position', [0.1, 0.1, 0.6, 0.8]);
    hold(ax, 'on');
    % Plot the data
    pl1 = scatter(X, Y);
    pl2 = plot(Xnew, Ypred, 'r-', 'LineWidth', 1.5); % regression line
    pl3 = plot(Xnew, CI(:,1), 'k--', 'LineWidth', 1.0); % lower bound
    pl4 = plot(Xnew, CI(:,2), 'k--', 'LineWidth', 1.0); % upper bound
    
    % Set grid, titles, and labels
    grid(ax, 'on');
    title(ax, 'Data with Fit and Confidence Intervals');
    xlabel(ax, 'X-Axis');
    ylabel(ax, 'Y-Axis');
    
    hold(ax, 'off');
    
    % Add the text to the figure
    % Using annotation or text for traditional figures
    htext = annotation(figlm, 'textbox', [0.7, 0.6, 0.2, 0.1],...
               'String', display_text,...
               'FitBoxToText', 'on');
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% ColumnManipulation.plotter parameters: mergedData dataMan.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/column_manipulateGUI.m#L229
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ColumnManipulation-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
mergedData = p.mergedData;
dataMan = p.dataMan;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/column_manipulateGUI.m:L229-L246
        figName = 'Acycle: Data Manipulate Plot';

        % Find any open figures with this name
        figs = findall(groot, 'Type', 'figure', 'Name', figName);

        if isempty(figs)
            % If no figure with the name exists, create it
            fig1 = figure('Name', figName);
        else
            % If it exists, clear the existing figure
            fig1 = figs(1); % In case there are multiple, take the first
            clf(fig1);
        end
        figure(fig1)
        plot(mergedData(:,1), dataMan)
        xlabel('X-Axis')
        ylabel('Y-Axis')
        title('Output')
%% End copied source
r=[];
end

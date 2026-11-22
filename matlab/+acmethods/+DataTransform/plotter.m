function [retval, id] = plotter(params, id)
% DataTransform.plotter parameters: data checkid yt j lambda.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L639
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DataTransform-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
checkid = p.checkid;
yt = p.yt;
j = p.j;
lambda = p.lambda;
dat=yt(:,checkid);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L639-L690
            fig_handle = findobj('Type', 'figure', 'Tag', 'fig_data_transf');
            if isempty(fig_handle)
                fig_handle = figure('Tag', 'fig_data_transf', 'Color', [1 1 1],'Name', 'Acycle: Data Transformations | Plot');
            else
                figure(fig_handle);
            end            
            
            coli = checkid(1); % use the first for plot
            % plot the raw data 
            if coli > 0
                x = data(:, 1);
                y = data(:, coli);

                subplot('Position', [0.05, 0.55, 0.6, 0.4]);
                plot(x, y);
                xlim([min(x), max(x)]);
                ylim([min(y), max(y)]);
                title('Raw data');
                ax = gca; 
                ax.XMinorTick = 'on'; 
                ax.YMinorTick = 'on';

                subplot('Position', [0.7, 0.55, 0.25, 0.4]);
                histfit(y, [], 'kernel');
                title('Raw data histogram');
                ax = gca; 
                ax.XMinorTick = 'on'; 
                ax.YMinorTick = 'on';
            end
            % transformed data
            subplot('Position', [0.05, 0.05, 0.6, 0.4]);
            plot(x,dat(:,1));
            xlim([min(x), max(x)]);
            try
                ylim([min(dat(:,1)), max(dat(:,1))]);
            catch
                error('Error using ylim in subplot(2,2,3). Results may have complex values???')
            end
            title('New data');
            if j == 13 % box-cox
                title(['BOX-COX Transformed Data. Best lambda: ', num2str(lambda)]);
            end
            ax = gca; 
            ax.XMinorTick = 'on'; 
            ax.YMinorTick = 'on';
            
            subplot('Position', [0.7, 0.05, 0.25, 0.4]);
            histfit(dat(:,1), [], 'kernel');
            title('Transformed data histogram');
            ax = gca; 
            ax.XMinorTick = 'on'; 
            ax.YMinorTick = 'on';
%% End copied source
r=[];
end

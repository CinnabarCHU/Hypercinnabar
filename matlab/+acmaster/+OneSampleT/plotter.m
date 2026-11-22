function [retval,id] = plotter(params,id)
% OneSampleT.plotter parameters: result.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/Unittest.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('OneSampleT-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
a = p.result; dof = a.dof; t = a.t; miu = a.miu; option_cal = a.option_cal;
ci_left = a.ci_left; t_critical = a.t_critical;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/Unittest.m:L238-L338
        %% Figure
        % Look for an existing figure with the name 'sf'
        fig1 = findobj('Type', 'figure', 'Name', 'Acycle: t test plot');
        % If no such figure exists, create a new one
        if isempty(fig1)
            fig1 = figure('Name', 'Acycle: t test plot','NumberTitle', 'off');
        else
            figure(fig1)
        end
        % Plot the t distribution in t-statistic units. The previous range
        % was based on the hypothesized mean (which has the data's units),
        % and an extreme observed t value could also trigger auto-scaling.
        % Both cases made the distribution appear as a narrow spike.
        if option_cal == 1
            criticalValues = [ci_left, t_critical];
        else
            criticalValues = t_critical;
        end
        baseHalfWidth = max(5, 1.2*max(abs(criticalValues)));
        if isfinite(t)
            plotHalfWidth = min(max(baseHalfWidth, 1.1*abs(t)), ...
                2*baseHalfWidth);
        else
            plotHalfWidth = baseHalfWidth;
        end
        x = linspace(-plotHalfWidth, plotHalfWidth, 1001);
        y = tpdf(x,dof);

        clf(fig1)
        ax = axes('Parent',fig1,'Tag','TTestAxes');
        distributionLine = plot(ax,x,y,'k-','LineWidth',1.25, ...
            'Tag','TTestDistribution');
        % The first plot resets axes properties while NextPlot is
        % 'replace', so restore the semantic tag after drawing it.
        set(ax,'Tag','TTestAxes');
        hold(ax,'on')

        % Use stable, distinguishable colors for the two critical limits.
        upperColor = [0, 0.4470, 0.7410];
        lowerColor = [0.8500, 0.3250, 0.0980];
        observedColor = [0.6350, 0.0780, 0.1840];

        legendHandles = gobjects(0);
        legendLabels = {};
        legendHandles(end+1) = distributionLine;
        legendLabels{end+1} = ['t distribution (dof = ',num2str(dof),')'];

        if option_cal == 1
            upperLine = xline(ax,t_critical,'--','Color',upperColor, ...
                'LineWidth',1.5,'Tag','TTestUpperCritical');
            lowerLine = xline(ax,ci_left,'--','Color',lowerColor, ...
                'LineWidth',1.5,'Tag','TTestLowerCritical');
            legendHandles(end+1) = upperLine;
            legendLabels{end+1} = ['Upper critical t = ', ...
                num2str(t_critical),' (95% CI)'];
            legendHandles(end+1) = lowerLine;
            legendLabels{end+1} = ['Lower critical t = ', ...
                num2str(ci_left),' (95% CI)'];
        elseif option_cal == 2
            criticalLine = xline(ax,t_critical,'--','Color',upperColor, ...
                'LineWidth',1.5,'Tag','TTestUpperCritical');
            legendHandles(end+1) = criticalLine;
            legendLabels{end+1} = ['Upper critical t = ', ...
                num2str(t_critical),' (alpha = 0.05)'];
        else
            criticalLine = xline(ax,t_critical,'--','Color',lowerColor, ...
                'LineWidth',1.5,'Tag','TTestLowerCritical');
            legendHandles(end+1) = criticalLine;
            legendLabels{end+1} = ['Lower critical t = ', ...
                num2str(t_critical),' (alpha = 0.05)'];
        end

        if ~isnan(t)
            observedPlotValue = t;
            observedOutsideRange = ~isfinite(t) || abs(t) > plotHalfWidth;
            if observedOutsideRange
                observedPlotValue = sign(t)*0.97*plotHalfWidth;
            end
            observedLine = xline(ax,observedPlotValue,'-','Color', ...
                observedColor,'LineWidth',1.75,'Tag','TTestObserved', ...
                'UserData',t);
            legendHandles(end+1) = observedLine;
            if observedOutsideRange
                legendLabels{end+1} = ['Observed t = ',num2str(t), ...
                    ' @ μ = ',num2str(miu),' (outside displayed range)'];
            else
                legendLabels{end+1} = ['Observed t = ',num2str(t), ...
                    ' @ μ = ',num2str(miu)];
            end
        end

        % Lock a symmetric range after adding reference lines so xline
        % cannot expand the axes and compress the probability density.
        xlim(ax,[-plotHalfWidth, plotHalfWidth])
        xlabel(ax,'t statistic')
        ylabel(ax,'Probability Density')
        legendObject = legend(ax,legendHandles,legendLabels, ...
            'Location','best');
        set(legendObject,'Tag','TTestLegend');
        title(ax,'Testing the mean: Student''s t distribution')
        hold(ax,'off')
%% End copied source
r = [];
end

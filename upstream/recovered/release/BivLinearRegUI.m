function BivLinearRegUI

    % Retrieve the instance of the first figure by its name
    uiFig1 = findobj(allchild(groot), 'flat', 'Name', 'Acycle: Data Table');
    
    if ~isempty(uiFig1)
        % Retrieve the data stored in the first figure
        selectedData = uiFig1.UserData;
        try
            if isempty(selectedData) || isnan(selectedData)
                warndlg('Warning: no data in Data Table selected')
                return
            end
        catch
        end
        if length(selectedData(:)) < 3
            return
        end
        
        [~, ncol] =size(selectedData);
        if ncol < 2
            warndlg('Warning: at least two columns in Data Table must be selected')
            return
        end
        
        tabcontent = {
            'Statistics', ...
            'ANOVA'};
        nn = 2;

        % look for an existing figure with the name 'Acycle: Two Sample Tests'
        figs = findobj(allchild(groot), 'flat', 'Name', 'Acycle: Linear Regression');
        % if no such uifigure
        
        if isempty(figs)
            % Create the figure
            fig = uifigure('Name', 'Acycle: Linear Regression', ...
                           'Position',[100 100 800 400]);
            
        else
            fig = figs(1);
            %clf(fig);
        end
        % 
        % % Create the tab group
        tabGroup = uitabgroup(fig);
        tabGroup.Position = [20 20 760 370];
        tabGroup.SelectionChangedFcn = @tabChangedCallback;

        % Create tabs
        tabs = gobjects(1, nn);  % Preallocate the array for tabs

        for i = 1:nn
            tabs(i) = uitab(tabGroup, 'Title', tabcontent{1,i}, 'UserData', i);
        end
        % 
        % % update tab
        tabChangedCallback;
    else
        warning('The Acycle: Data Table does not exist or has not been created yet.');
    end
    
end

% Define the tab changed callback function
function tabChangedCallback(src, event)

    fig = findobj(allchild(groot), 'flat', 'Name', 'Acycle: Linear Regression');

    try
        % Get the selected tab
        selectedTab = event.NewValue;
        % Retrieve the user data (tab index)
        tabIndex = selectedTab.UserData;
    catch  % default tab index == 1; t test
        tabIndex = 1;
    end
    
    % Here you can add more complex actions that you want to execute when each tab is clicked.
    % Extract the data from each group
    
    uiFig1 = findobj(allchild(groot), 'flat', 'Name', 'Acycle: Data Table');
    
    selectedData = uiFig1.UserData;
    X = selectedData(:,1);
    Y = selectedData(:,2);

    % Fit a linear regression model by using fitlm.
    % Combine into a table, which is required for the fitlm function
    tbl = table(X,Y);
    
    % Fit linear regression model
    lm = fitlm(tbl, 'linear');
    % Get the confidence intervals
    confidenceIntervals = coefCI(lm, 0.05); % 0.05 significance level for 95% CI
    % The first row corresponds to the intercept, and the second row corresponds to the slope.
    interceptCI = confidenceIntervals(1, :);
    slopeCI = confidenceIntervals(2, :);

    % Display the summary of the Linear Model
    disp(lm);
    %figure;plot(lm)
    % Calculate the confidence intervals for the regression line
    % Creating a sequence of x values spanning the range of your data
    Xnew = linspace(min(X), max(X), 100)';
    
    % Convert Xnew to a table with the same variable name as the original data
    Xnew_table = array2table(Xnew, 'VariableNames', {'X'}); % the name 'X' should match the name of your predictor in the original table
    
    % Use the predict function to generate confidence intervals
    [Ypred, CI] = predict(lm, Xnew_table, 'Alpha', 0.05); % 95% confidence interval
    % Getting the coefficients (intercept and slope) of the regression equation
    coefficients = lm.Coefficients;
    intercept = coefficients.Estimate(1);
    slope = coefficients.Estimate(2);
    
    % Getting the R-squared value
    Rsq = lm.Rsquared.Ordinary;
    
    % Getting the p-value of the hypothesis test that each coefficient is zero
    pValues = coefficients.pValue; % returns a p-value for each coefficient
    ModelFitV = lm.ModelFitVsNullModel;
    pvalue = ModelFitV.Pvalue;
    % Create the string for display
    regression_eq = sprintf('Y = %.6f + %.6f*X', intercept, slope);
    Rsq_text = sprintf('R-squared = %.6f', Rsq);
    p_text = sprintf('p-value = %.6f', pvalue);
    display_text = sprintf('Regression equation: \n%s\n%s\n%s', regression_eq, Rsq_text, p_text);
    
    %% Plot the data, fit line, and confidence bounds
    % Find or create the figure
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

    %% tabIndex 1: fitlm
    if tabIndex == 1
        
        multilineText = {''
            'Linear regression: '
            ''
            ['Number Obser: ',sprintf('%6.0d', lm.NumObservations)]
            ['        RMSE:',sprintf('%10.6f', lm.RMSE), '          (Root Mean Squared Error)']
            ''
            ['     slope a: ', sprintf('%10.6f', slope),'          Std. error a: ', sprintf('%10.6f', coefficients.SE(2))]
            ['           t: ', sprintf('%10.6f', coefficients.tStat(2)),'             p (slope): ',  sprintf('%10.6f', coefficients.pValue(2))]
            ['95% Conf Int: [',sprintf('%10.6f', slopeCI(1)), ' ', sprintf('%10.6f', slopeCI(2)),']']
            ''
            [' Intercept b: ', sprintf('%10.6f', intercept),'          Std. error b: ',sprintf('%10.6f', coefficients.SE(1))]
            ['           t: ', sprintf('%10.6f', coefficients.tStat(1)),'         p (intercept): ',  sprintf('%10.6f', coefficients.pValue(2))]
            ['95% Conf Int: [',sprintf('%10.6f', interceptCI(1)), ' ', sprintf('%10.6f', interceptCI(2)),']']
            ''
            ''
            'Correlation:'
            ''
            ['                             r: ', sprintf('%10.7f', sqrt(Rsq)), ...
             '            r-squared: ', sprintf('%10.7f', Rsq)]
            ['                    Adjusted r: ', sprintf('%10.7f', sqrt(lm.Rsquared.Adjusted)), ...
             '   Adjusted r-squared: ', sprintf('%10.7f', lm.Rsquared.Adjusted)]
            ['F-statistic vs. constant model: ', sprintf('%10.7f', lm.ModelFitVsNullModel.Fstat)]
            ['                       p value: ', sprintf('%10.7f', lm.ModelFitVsNullModel.Pvalue)]
        };

    else

        if tabIndex == 2
            multilineText = {
                ''
                'Analysis of variance (ANOVA) test'
                ''
                '                SumOfSquares    DF     MeanSquare         F           pValue'
                '               --------------  ----   ------------       ---         --------'
                ['       Total: ', sprintf('%10.6f', lm.SST),'    ', ...
                    sprintf('%5.0d', lm.NumObservations-1),'    ', sprintf('%10.6f', (lm.SST)/(lm.NumObservations-1))]
                ['       Model: ', sprintf('%10.6f', lm.SSR),'    ', ...
                    sprintf('%5.0d', 1),'    ', sprintf('%10.6f', lm.SSR), '     ', ...
                    sprintf('%10.6f', lm.ModelFitVsNullModel.Fstat), '    ', sprintf('%10.6f', lm.ModelFitVsNullModel.Pvalue)]
                ['    Residual: ', sprintf('%10.6f', lm.SSE),'    ', ...
                    sprintf('%5.0d', lm.DFE),'    ', sprintf('%10.6f', lm.SSE/lm.DFE)]
            }; 
        end

    end
    
    %    Create a textarea to display the text
    txtArea = uitextarea(fig,...
        'Position', [20, 20, 760, 345],... % Position and size of the text area
        'Value','',...
        'FontSize', 14,...                 % Set font size
        'Editable', 'off',...              % Make it read-only; text can be selected but not changed
        'HorizontalAlignment', 'Left',...  % Optional: Set horizontal alignment
        'BackgroundColor', 'w');  
    try 
        txtArea.FontName = 'Courier'; 
    catch
    end
    txtArea.Value = ''; pause(0.01);txtArea.Value = ''; pause(0.01);txtArea.Value = ''; pause(0.01);
    txtArea.Value = multilineText;
end

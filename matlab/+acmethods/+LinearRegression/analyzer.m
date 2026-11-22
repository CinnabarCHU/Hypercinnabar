function [retval, id] = analyzer(params, id)
% LinearRegression.analyzer parameters: selectedData.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8941
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LinearRegression-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
selectedData=p.selectedData;
%% Copied from Acycle-MATLAB-distribution@54720f36678812cca5e6286efaf91433b37047589dd2ee994049ea5020ca35dc Acycle_3.1.1/code/test/BivLinearRegUI.m:L85-L128
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
%% End copied source
%% Copied from Acycle-MATLAB-distribution@54720f36678812cca5e6286efaf91433b37047589dd2ee994049ea5020ca35dc Acycle_3.1.1/code/test/BivLinearRegUI.m:L167-L190
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
%% End copied source
statistics=multilineText;
%% Copied from Acycle-MATLAB-distribution@54720f36678812cca5e6286efaf91433b37047589dd2ee994049ea5020ca35dc Acycle_3.1.1/code/test/BivLinearRegUI.m:L195-L208
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
%% End copied source
anovaText=multilineText;
r = struct();
r.X = X;
r.Y = Y;
r.Xnew = Xnew;
r.Ypred = Ypred;
r.CI = CI;
r.interceptCI = interceptCI;
r.slopeCI = slopeCI;
r.intercept = intercept;
r.slope = slope;
r.Rsq = Rsq;
r.pvalue = pvalue;
r.pValues = pValues;
r.display_text = display_text;
r.statistics = statistics;
r.anovaText = anovaText;
r.coefficients=table2struct(coefficients);
end

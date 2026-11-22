function [retval, id] = analyzer(params, id)
% TwoSampleTests.analyzer parameters: selectedData tabIndex.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/UniTwoSampleTestsUI.m#L96
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('TwoSampleTests-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
selectedData = p.selectedData;
tabIndex = p.tabIndex;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniTwoSampleTestsUI.m:L96-L342
    group1 = selectedData(:, 1);
    group2 = selectedData(:, 2);
    group1 = group1(~isnan(group1)); % remove empty cell
    group2 = group2(~isnan(group2)); % remove empty cell
    %% tabIndex 1: t test
    if tabIndex == 1
        % Perform the t-test
        [h1, p1, ci1, stats1] = ttest(group1);
        [h2, p2, ci2, stats2] = ttest(group2);
        [h, p, ci, stats] = ttest2(group1, group2);
        
        multilineText = {
            ''
            'T test for equal means'
            ''
            'The first sample A                            The second sample B'
            ['N: ', sprintf('%10.0f', length(group1)),'                                 ',...
             'N: ', sprintf('%10.0f', length(group2))]
            ['Mean: ',sprintf('%10.6f', mean(group1)),'                              ',...
             'Mean: ',sprintf('%10.6f', mean(group2))]
            ['Conf. Interval: [', sprintf('%10.6f', ci1(1)),'  ',sprintf('%10.6f', ci1(2)),']','      ',...
             'Conf. Interval: [', sprintf('%10.6f', ci2(1)),'  ',sprintf('%10.6f', ci2(2)),']']
            ''
            ['Difference in means: ',num2str(mean(group1) - mean(group2))]
            ['Confidence Interval of the difference in means: [', num2str(ci(1)),'  ', num2str(ci(2)),']']
            ''
            ['T-statistic = ', num2str(stats.tstat)]
            ['Degrees of Freedom = ', num2str(stats.df)]
            ['P-value (same mean) = ', num2str(p)]
            ''
            'CONCLUSION:'
            ''
            ''
        }; 
            % Define the text with multiple lines
            if h == 1
                multilineText{18,1} = 'Reject the null hypothesis (equal means) at the 5% significance level.';
            else
                multilineText{18,1} = 'Accept the null hypothesis (equal means) at the 5% significance level.';
            end
    %% tabIndex 2: f test
    elseif tabIndex == 2
        
        for i = 1:2
            if i == 1
                dat1 = group1;
            else 
                dat1 = group2;
            end
            % Sample size
            n = length(dat1);
            % Sample variance
            s2 = var(dat1, 1); % Note: using 1 for the W parameter to get the unbiased estimate
            % Confidence level, typically 0.95 for 95%
            confLevel = 0.95;
            % Calculate the confidence interval for the variance
            alpha = 1 - confLevel;
            chi2_lower = chi2inv(alpha/2, n-1);
            chi2_upper = chi2inv(1 - alpha/2, n-1);
            var_lower = ((n-1) * s2) / chi2_upper;
            var_upper = ((n-1) * s2) / chi2_lower;
            
            var2(i,1) = var_lower;
            var2(i,2) = var_upper;
        end
        
        % test 2 samples
        [h, p, ci, stats] = vartest2(group1, group2);
        
        
        multilineText = {
            ''
            'F test for equal variances'
            ''
            'The first sample A                            The second sample B'
            ['N: ', sprintf('%10.0f', length(group1)),'                                 ',...
             'N: ', sprintf('%10.0f', length(group2))]
            ['Degree of freedom (DOF): ', sprintf('%5.0f', stats.df1),'                ',...
             'DOF: ', sprintf('%8.0f', stats.df2)]
            ['Variance: ',sprintf('%10.6f', var(group1)),'                          ',...
             'Variance: ',sprintf('%10.6f', var(group2))]
            ['Conf. Interval: [', sprintf('%10.6f', var2(1,1)),'  ',sprintf('%10.6f', var2(1,2)),']','      ',...
             'Conf. Interval: [', sprintf('%10.6f', var2(2,1)),'  ',sprintf('%10.6f', var2(2,2)),']']
            ''
            ['Difference in variance: ',num2str(abs(var(group1) - var(group2)))]
            ''
            ['F-statistic = ', num2str(stats.fstat)]
            ['Confidence Interval for the ratio of the variances: [', num2str(ci(1)),'  ', num2str(ci(2)),']']
            ['P-value (same variance) = ', num2str(p)]
            ''
            'CONCLUSION:'
            ''
            ''
        }; 
        % Display the results
        if h == 0
            multilineText{18,1} = 'Do not reject the null hypothesis that the variances are equal at the 5% significance level.';
        else
            multilineText{18,1} = 'Reject the null hypothesis that the variances are equal at the 5% significance level.';
        end
        
    %% tabIndex 3: Mann-Whitney U test
    elseif tabIndex == 3
        % Perform the Mann-Whitney U test
        % a nonparametric test of the null hypothesis that 
        % it is equally likely that a randomly selected value from one population 
        % will be less than or greater than a randomly selected value from a
        % second population. This test does not assume a normal distribution 
        % and is used when comparing two samples that are independent, 
        % but not necessarily of the same size.
        [p, h, stats] = ranksum(group1, group2);
        
        % Pool the data
        pooledData = [group1; group2];

        % Get the ranks of the pooled data
        ranks = tiedrank(pooledData);  % 'tiedrank' handles ties appropriately

        % Determine the ranks for each group
        ranks_group1 = ranks(1:length(group1));
        ranks_group2 = ranks(length(group1)+1:end);

        % Compute the sum of ranks for each group
        sumRanks_group1 = sum(ranks_group1);
        sumRanks_group2 = sum(ranks_group2);

        % Compute the U statistic for each group
        u1 = sumRanks_group1 - (length(group1)*(length(group1)+1))/2;
        u2 = sumRanks_group2 - (length(group2)*(length(group2)+1))/2;

        % The U statistic is the smaller of u1 and u2
        U = min(u1, u2);

        % Compute the median rank for each group
        medianRank_group1 = median(ranks_group1);
        medianRank_group2 = median(ranks_group2);
        
        multilineText = {
            ''
            'Mann-Whitney U test for equal medians'
            ''
            'The first sample A                            The second sample B'
            ['N: ', sprintf('%15.0f', length(group1)),'                            ',...
             'N: ', sprintf('%15.0f', length(group2))]
            ''
            ['Mann-Whitney U: ', sprintf('%10.6f', U)]
            ['             z: ', sprintf('%10.6f', stats.zval)]
            ''
            ['P-value (same variance) = ', num2str(p)]
            ''
            'CONCLUSION:'
            ''
            ''
        }; 
    
        if h == 0
            multilineText{14,1} = 'Do not reject the null hypothesis at the 5% significance level';
        else
            multilineText{14,1} = 'Reject the null hypothesis at the 5% significance level';
        end
    %%  Kolmogorov–Smirnov
    elseif tabIndex == 4
        
        [h,p,ks2stat] = kstest2(group1, group2);
        
        multilineText = {
            ''
            'Two-sample Kolmogorov–Smirnov test for same continuous distribution'
            ''
            'The first sample A                            The second sample B'
            ['N: ', sprintf('%15.0f', length(group1)),'                            ',...
             'N: ', sprintf('%15.0f', length(group2))]
            ''
            ['Kolmogorov–Smirnov statistic: ', sprintf('%10.6f', ks2stat)]
            ''
            ['P-value (same variance) = ', num2str(p)]
            ''
            'CONCLUSION:'
            ''
            ''
        }; 
        
    
        if h == 0
            multilineText{13,1} = 'Do not reject the null hypothesis at the 5% significance level';
        else
            multilineText{13,1} = 'Reject the null hypothesis at the 5% significance level';
        end
    %%  Anderson–Darling test
    elseif tabIndex == 5
        % prepare data
        X1 = [group1, ones(length(group1),1)];  
        X2 = [group2, ones(length(group2),1)*2];
        X = [X1;X2]; 
        AnDarksamtest1 = AnDarksamtest(X);
        alpha = 0.05;
        
        multilineText = {
            ''
            'K-sample Anderson-Darling test for same continuous distribution'
            ''
            'The first sample A                            The second sample B'
            ['N: ', sprintf('%15.0f', length(group1)),'                            ',...
             'N: ', sprintf('%15.0f', length(group2))]
            ['Number of ties (identical values): ', sprintf('%6.0f', AnDarksamtest1.nties)]
            ['Mean of the Anderson-Darling rank statistic: ', sprintf('%10.6f', AnDarksamtest1.meanADRstat)]
            ['Standard deviation of the Anderson-Darling rank statistic: ', sprintf('%10.6f', AnDarksamtest1.stdADRstat)]
            ''
            '- - - - - - - - - - - - - - - - - - - - - '
            'Not adjusted for ties' % line 10
            ['Anderson-Darling rank statistic: ', sprintf('%10.6f', AnDarksamtest1.ADKn)]
            ['Standardized Anderson-Darling rank statistic: ', sprintf('%10.6f', AnDarksamtest1.ADKsn)]
            ['Probability associated to the Anderson-Darling rank statistic = ', sprintf('%10.6f', AnDarksamtest1.Pn)]
            ''
            'CONCLUSION:'
            ['With a given significance p-value = ', sprintf('%3.4f', alpha)]
            ''
            '' 
            ''
            '- - - - - - - - - - - - - - - - - - - - - '
            'Adjusted for ties'
            ['Anderson-Darling rank statistic: ', sprintf('%10.6f', AnDarksamtest1.ADK)]
            ['Standardized Anderson-Darling rank statistic: ', sprintf('%10.6f', AnDarksamtest1.ADKs)]  % line 21
            ['Probability associated to the Anderson-Darling rank statistic = ', sprintf('%10.6f', AnDarksamtest1.P)]
            ''
            'CONCLUSION:'
            ['With a given significance p-value = ', sprintf('%3.4f', alpha)]
            ''
            ''
            ''
        }; 
        
        if AnDarksamtest1.Pn >= alpha
            multilineText{19,1} = 'The populations from which the k-samples of data were drawn are identical:';
            multilineText{20,1} = 'natural groupings have no significant effect (unstructurated).';
        else
            multilineText{19,1} = 'The samples were drawn from different populations: data may be considered'; 
            multilineText{20,1} = 'structurated with respect to the random of fixed effect in question.';
        end
        
        if AnDarksamtest1.P >= alpha
            multilineText{29,1} = 'The populations from which the k-samples of data were drawn are identical:';
            multilineText{30,1} = 'natural groupings have no significant effect (unstructurated).';
        else
            multilineText{29,1} = 'The samples were drawn from different populations: data may be considered'; 
            multilineText{30,1} = 'structurated with respect to the random of fixed effect in question.';
        end
%% End copied source
else, error('Acycle:TwoSample:Tab','Expected tab 1 through 5.'); end
r = struct();
r.multilineText = multilineText;
end

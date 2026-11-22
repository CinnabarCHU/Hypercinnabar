function [retval, id] = analyzer(params, id)
% OneSampleT.analyzer parameters: data miu option_cal.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/Unittest.m#L110
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('OneSampleT-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
miu = p.miu;
option_cal = p.option_cal;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/Unittest.m:L110-L110
        a = data(:);  % force
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/Unittest.m:L122-L226
        a_mean = mean(a);
        % std
        std_dev = std(a);
        % number of data points
        n = length(a);
        % degree of freedom
        dof = n-1;
        
        % t value
        t = (a_mean - miu)/(std_dev * sqrt(1/n));
        
        if option_cal == 1  % compare means = 
            alpha = 0.025;  % (two-tailed)
        elseif option_cal == 2
            alpha = 0.05;  % one tailed
        elseif option_cal == 3
            alpha = 0.05;  % one tailed
        end
        
        % Find the critical t-value (two-tailed)
        t_critical = tinv(1-alpha, dof); % 0.975 because the 2.5% in the upper tail and 2.5% in the lower tail
        
        % Calculate the standard error of the mean
        sem = std_dev / sqrt(n);

        % Calculate the margin of error
        margin_of_error = t_critical * sem;

        % Calculate the confidence intervals
        ci_lower = a_mean - margin_of_error;  
        ci_upper = a_mean + margin_of_error;

        if option_cal == 1  % compare means = 
            % inverse CDF
            ci_left = tinv(0.025,dof);
            p = 2 * (1 - tcdf(abs(t), dof));
            
            if p<=0.05
                stat1 = 'Means are significantly different';
            else
                stat1 = 'Means are not significantly different';
            end
            
            stats = { '                  N:', num2str(length(a));
                      '         Given Mean:', num2str(miu);
                      '        Sample Mean:', num2str(a_mean);
                      ' 95% conf. interval:', [num2str(ci_lower),' - ',num2str(ci_upper)];
                      ' ', '';
                      '         Difference:', num2str(abs(miu - a_mean));
                      ' 95% conf. interval:', [num2str(ci_lower-miu),' - ',num2str(ci_upper-miu)];
                      ' ', '';
                      '                  t:', num2str(t);
                      'p value (same mean):', num2str(p);
                      '','';
                      '         Conclusion:',stat1};
                  
        elseif option_cal == 2  % compare means
            % Find the critical t-value (one-tailed)
            %t = abs(t);
            if t > t_critical
                stat1 = ['Reject H0: u <= ', num2str(miu),'; Accept H1: u > ', num2str(miu)];
            else
                stat1 = ['Accept H0: u <= ', num2str(miu),'; Reject H1: u > ', num2str(miu)];
            end
            % one side, thus p-value = 0.05
            p =  1-tcdf(t, dof);
            
            stats = { '                  N:', num2str(length(a));
                      '         Given Mean:', num2str(miu);
                      '        Sample Mean:', num2str(a_mean);
                      ' 95% conf. interval:', num2str(ci_lower);
                      ' ', '';
                      '         Difference:', num2str(abs(miu - a_mean));
                      ' 95% conf. interval:', num2str(ci_upper-miu);
                      ' ', '';
                      '                  t:', num2str(t);
                      'p value (same mean):', num2str(p);
                      '','';
                      '         Conclusion:',stat1};
                  
        elseif option_cal == 3  % compare means
            % Find the critical t-value (one-tailed)
            t_critical = tinv(0.05, dof);
            if t < t_critical
                stat1 = ['Reject H0: u >= ', num2str(miu),'; Accept H1: u < ', num2str(miu)];
            else
                stat1 = ['Accept H0: u >= ', num2str(miu),'; Reject H1: u < ', num2str(miu)];
            end
            % one side, thus p-value = 0.05
            p =  tcdf(t, dof);
            
            stats = { '                  N:', num2str(length(a));
                      '         Given Mean:', num2str(miu);
                      '        Sample Mean:', num2str(a_mean);
                      ' 95% conf. interval:', num2str(ci_upper);
                      ' ', '';
                      '         Difference:', num2str(abs(miu - a_mean));
                      ' 95% conf. interval:', num2str(ci_lower-miu);
                      ' ', '';
                      '                  t:', num2str(t);
                      'p value (same mean):', num2str(p);
                      '','';
                      '         Conclusion:',stat1};
                  
        end
%% End copied source
if option_cal == 1, ci = ci_left; else, ci = []; end
r = struct();
r.ci_left = ci;
r.stats = stats;
r.t = t;
r.dof = dof;
r.t_critical = t_critical;
r.miu = miu;
r.option_cal = option_cal;
end

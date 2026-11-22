function [retval, id] = analyzer(params, id)
% Normality.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/UniNormalityUI.m#L45
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Normality-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniNormalityUI.m:L45-L114
        data = data(:);  % force
        data = data(~isnan(data)); % remove empty cell
        alpha = 0.05;
        % Shapiro-Wilk parametric hypothesis test
        [H, pValue, W] = swtest(data, alpha);
        % Lilliefors test
        [h,p,kstat,critval] = lillietest(data);
        % Anderson-Darling Test
        [ha,pa,adstata,cva] = adtest(data);
        % Kolmogorov-Smirnov Test
        % kstest tests for a standard normal distribution by default
        [hk,pk,ksstat,cvk] = kstest(zscore(data));
        
        % Chi-square test
        [hc, pc, statsc] = chi2gof(data);

        stats = { 'Number (N)', sprintf('%5.0d', length(data)) ;
                  'Shapiro-Wilk', sprintf('%10.6f', W) ;
                  'p value', sprintf('%10.6f', pValue);
                  'Conclusion', '';
                  '','';
                  'Lilliefors',sprintf('%10.6f', kstat);
                  'Critical Value',sprintf('%10.6f', critval);
                  'p value', sprintf('%10.6f', p);
                  'Conclusion','';
                  '','';
                  'Anderson-Darling',sprintf('%10.6f', adstata);
                  'Critical Value',sprintf('%10.6f', cva);
                  'p value',sprintf('%10.6f', pa);
                  'Conclusion','';
                  '','';
                  'Kolmogorov-Smirnov',sprintf('%10.6f', ksstat);
                  'Critical Value',sprintf('%10.6f', cvk);
                  'p value',sprintf('%10.6f', pk);
                  'Conclusion','';
                  '','';
                  'Chi-square goodness-of-fit',sprintf('%10.6f', statsc.chi2stat) ;
                  'degree of freedom',sprintf('%10.0d', statsc.df) ;
                  'p value', sprintf('%10.6f', pc);
                  'Conclusion',''};
              
        state1 = 'Normal distribution';
        state0 = 'Not normal';
        if H == 0
            stats{4,2} = state1;
        else
            stats{4,2} = state0;
        end
        if h == 0
            stats{9,2} = state1;
        else
            stats{9,2} = state0;
        end
        if ha == 0
            stats{14,2} = state1;
        else
            stats{14,2} = state0;
        end
        
        if hk == 0
            stats{19,2} = state1;
        else
            stats{19,2} = state0;
        end
        
        if hc == 0
            stats{24,2} = state1;
        else
            stats{24,2} = state0;
        end
%% End copied source
r = struct();
r.stats = stats;
end

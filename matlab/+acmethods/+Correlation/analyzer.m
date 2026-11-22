function [retval, id] = analyzer(params, id)
% Correlation.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/BivCorrUI.m#L63
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Correlation-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/BivCorrUI.m:L63-L98
        [R, P, RL, RU] = corrcoef(data); % R is the correlation matrix, and P is the matrix of p-values
        % Spearman
        [SpearmanRho, SpearmanPValue] = corr(data(:,1), data(:,2), 'Type', 'Spearman');
        % Kendall Tau
        [KendallTau, KendallPValue] = corr(data(:,1), data(:,2), 'Type', 'Kendall');

        stats = { 'Number (N)', sprintf('%8.0d', length(data)) ;
                  'Pearson r', sprintf('%10.6f', R(1,2));
                  'Pearson r 95% CI', sprintf('[%10.6f  %10.6f]', RL(1,2), RU(1,2));
                  'Pearson p', sprintf('%10.6f', P(1,2));
                  'Conclusion','';
                  '','';
                  'Spearman r',sprintf('%10.6f', SpearmanRho);
                  'Spearman p Value',sprintf('%10.6f', SpearmanPValue);
                  'Conclusion','';
                  '','';
                  'Kendall Tau',sprintf('%10.6f', KendallTau);
                  'Kendall p value',sprintf('%10.6f', KendallPValue);
                  'Conclusion',''};
        state1 = 'Corr. is significant';
        state2 = 'Corr. is not significant';
        if P(1,2) < 0.05
            stats{5,2} = state1;
        else
            stats{5,2} = state2;
        end
        if SpearmanPValue < 0.05
            stats{9,2} = state1;
        else
            stats{9,2} = state2;
        end
        if KendallPValue < 0.05
            stats{13,2} = state1;
        else
            stats{13,2} = state2;
        end
%% End copied source
r = struct();
r.stats = stats;
end

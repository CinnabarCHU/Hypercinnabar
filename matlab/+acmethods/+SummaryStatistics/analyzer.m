function [retval, id] = analyzer(params, id)
% SummaryStatistics.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/UniStatisticSum.m#L41
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SummaryStatistics-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniStatisticSum.m:L41-L59
        data = data(:);  % force
        data = data(~isnan(data)); % remove empty cell
        stats = { 'Number (N)', sprintf('%10.0d', length(data)) ;
                  'Min', sprintf('%10.6f', min(data));
                  'Max', sprintf('%10.6f', max(data));
                  'Sum', sprintf('%10.6f', sum(data));
                  'Mean', sprintf('%10.6f', mean(data));
                  'Variance', sprintf('%10.6f', var(data));
                  'Standard Deviation', sprintf('%10.6f', std(data));
                  'Median', sprintf('%10.6f', median(data));
                  ' 2.5th Percentile', sprintf('%10.6f', prctile(data, 2.5));
                  '   5th Percentile', sprintf('%10.6f', prctile(data, 5));
                  '  25th Percentile', sprintf('%10.6f', quantile(data, 0.25));
                  '  75th Percentile', sprintf('%10.6f', quantile(data, 0.75));
                  '  95th Percentile', sprintf('%10.6f', prctile(data, 95));
                  '97.5th Percentile', sprintf('%10.6f', prctile(data, 97.5));
                  'Mode', sprintf('%10.6f', mode(data));
                  'Skewness', sprintf('%10.6f', skewness(data));
                  'Kurtosis', sprintf('%10.6f', kurtosis(data))};
%% End copied source
r = struct();
r.stats = stats;
end

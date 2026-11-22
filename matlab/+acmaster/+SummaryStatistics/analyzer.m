function [retval,id] = analyzer(params,id)
% SummaryStatistics.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/UniStatisticSum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SummaryStatistics-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
r = calculateStatistics(p.data);
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/UniStatisticSum.m:L47-L71
    function stats = calculateStatistics(data)
        data = data(:);  % force
        data = data(isfinite(data)); % remove empty cell
        if isempty(data)
            stats = {'Number (N)', '0'};
            return
        end
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
    end
%% End copied source

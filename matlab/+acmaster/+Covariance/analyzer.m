function [retval,id] = analyzer(params,id)
% Covariance.analyzer parameters: data n_bootstraps.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/BivCovUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Covariance-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
n_bootstraps = p.n_bootstraps;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/BivCovUI.m:L79-L79
        c = cov(data); % c
%% End copied source
if n_bootstraps < 100 || ~isfinite(n_bootstraps), error('Acycle:Covariance:Samples','Expected at least 100 bootstrap samples.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/BivCovUI.m:L90-L108
        alpha = 0.05;
        cov_bootstraps = zeros(n_bootstraps, 1); % pre-allocate for speed
        
        for i = 1:n_bootstraps
            sample_indices = randi([1, size(data, 1)], size(data, 1), 1);
            bootstrap_sample = data(sample_indices, :);
            cov_matrix = cov(bootstrap_sample(:, 1), bootstrap_sample(:, 2));
            cov_bootstraps(i) = cov_matrix(1,2); % store the covariance value, not the matrix
        end
        
        % Calculate confidence interval
        CI_lower = prctile(cov_bootstraps, 100 * (alpha / 2));
        CI_upper = prctile(cov_bootstraps, 100 * (1 - alpha / 2));
        
        CI = [CI_lower, CI_upper]; 

        stats = { 'Number (N)', sprintf('%8.0d', length(data)) ;
                  'Covariance', sprintf('%10.6f', c(1,2));
                  '95% CI', sprintf('[%10.6f  %10.6f]', CI_lower, CI_upper)};
%% End copied source
r = struct();
r.stats = stats;
r.c = c;
r.CI = CI;
end

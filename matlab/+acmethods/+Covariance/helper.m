function [retval, id] = helper(params, id)
% Covariance.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/BivCovUI.m#L83
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Covariance-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/BivCovUI.m:L83-L83
            n_bootstraps = 10000;
%% End copied source
r = struct();
r.data = data;
r.n_bootstraps = n_bootstraps;
end

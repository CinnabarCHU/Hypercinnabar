function [retval,id] = helper(params,id)
% Covariance.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/BivCovUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Covariance-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/BivCovUI.m:L83-L83
            n_bootstraps = 10000;
%% End copied source
r = struct();
r.data = data;
r.n_bootstraps = n_bootstraps;
end

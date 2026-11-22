function [retval, id] = helper(params, id)
% bayes_cpt_r2.helper parameters: data k_max d_min k_0 v_0 sig_0 num_samp.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/bayes_changepoint/bayes_cpt_r2.m#L66
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('bayes_cpt_r2-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'k_max', 'd_min', 'k_0', 'v_0', 'sig_0', 'num_samp'}, 5, @legacyDefaults);
end

function values = legacyDefaults(data, k_max, d_min, k_0, v_0, sig_0, num_samp)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/bayes_changepoint/bayes_cpt_r2.m:L66-L74
if nargin > 7
    error('Too much input')
end
if nargin < 7
    num_samp = 500;
    if nargin < 6
        sig_0 = var(data(:,2));
    end
end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('k_max', 'var'), values.k_max = k_max; end
if exist('d_min', 'var'), values.d_min = d_min; end
if exist('k_0', 'var'), values.k_0 = k_0; end
if exist('v_0', 'var'), values.v_0 = v_0; end
if exist('sig_0', 'var'), values.sig_0 = sig_0; end
if exist('num_samp', 'var'), values.num_samp = num_samp; end
end

function [retval,id] = helper(params,id)
% bayes_cpt.helper parameters: data k_max d_min k_0 v_0 sig_0 num_samp.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/bayes_cpt.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bayes_cpt-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'k_max', 'd_min', 'k_0', 'v_0', 'sig_0', 'num_samp'}, 5, @legacyDefaults);
end

function values = legacyDefaults(data, k_max, d_min, k_0, v_0, sig_0, num_samp)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/bayes_changepoint/bayes_cpt.m:L65-L73
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

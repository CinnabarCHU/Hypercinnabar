function [retval, id] = analyzer(params, id)
% Lyapunov.analyzer parameters: data_even tau window step_size num_surrogates.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9805
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lyapunov-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data_even = p.data_even;
tau = p.tau;
window = p.window;
step_size = p.step_size;
num_surrogates = p.num_surrogates;
do_plot=0;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9805-L9805
                            output = lyapunov_timeseries(data_even, tau, window, step_size, num_surrogates, do_plot);
%% End copied source
r = struct();
r.output = output;
end

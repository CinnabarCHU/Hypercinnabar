function [retval, id] = analyzer(params, id)
% Lyapunov.analyzer parameters: data or data_even interpolate_rate padtype tau window step_size num_surrogates.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9805
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lyapunov-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
options=p;
if isfield(p,'data_even')
    data_even=p.data_even; data=data_even;
else
    data=p.data; interpolate_rate=p.interpolate_rate; padtype=p.padtype; window=p.window;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9795-L9795
                            p = polyfit(data(:,1), data(:,2), 1);          % p(1) = slope, p(2) = intercept
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9797-L9803
                            data(:,2) = data(:,2) - polyval(p, data(:,1));

                            [data_even] = interpolate(data,interpolate_rate);

                            if padtype > 0
                                data_even = zeropad2(data_even,window,padtype);
                            end
%% End copied source
end
tau = options.tau;
window = options.window;
step_size = options.step_size;
num_surrogates = options.num_surrogates;
do_plot=0;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9805-L9805
                            output = lyapunov_timeseries(data_even, tau, window, step_size, num_surrogates, do_plot);
%% End copied source
r = struct();
r.output = output; r.data=data;
end

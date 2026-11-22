function [retval, id] = helper(params, id)
% Lyapunov.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9756
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lyapunov-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data=p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9756-L9762
                    t = data(:,1);
                    samplerate = diff(t);
                    interpolate_rate = median(samplerate);
                    ndata = length(t);
                    datalength = data(length(t),1)-data(1,1);
                    samp95 = prctile(samplerate,95);  % new version; 1-2 * sample 95% percentile
                    samp05 = prctile(samplerate,5);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9766-L9770
                        if 0.3 * datalength > 400
                            window1 = 400;
                        else
                            window1 = 0.3 * datalength;
                        end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9784-L9784
                        defaultans = {num2str(samp95),num2str(window1),num2str(samp95), '0', '0'};
%% End copied source
answer=defaultans;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9788-L9793
                            tau  = str2double(answer{1});
                            window = str2double(answer{2});
                            step_size = str2double(answer{3});
                            num_surrogates = str2double(answer{4});
                            padtype= str2double(answer{5});
                            do_plot = false;
%% End copied source
r = struct();
r.data = data;
r.interpolate_rate = interpolate_rate;
r.tau = tau;
r.window = window;
r.step_size = step_size;
r.num_surrogates = num_surrogates;
r.padtype = padtype;
r.unit=''; r.unit_type=0;
end

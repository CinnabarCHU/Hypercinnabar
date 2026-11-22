function [retval, id] = analyzer(params, id)
% LyapunovMonteCarlo.analyzer parameters: data nsim tau1 tau2 window1 window2 samprate1 samprate2 nout step_size padtype.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9924
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LyapunovMonteCarlo-v1.0/analyzer', params, id, @execute);
end

function [r, status] = execute(p)
data = p.data;
nsim = p.nsim;
tau1 = p.tau1;
tau2 = p.tau2;
window1 = p.window1;
window2 = p.window2;
samprate1 = p.samprate1;
samprate2 = p.samprate2;
nout = p.nout;
step_size = p.step_size;
padtype = p.padtype;
if nsim<50, r=[]; status='cancelled'; return; end
status='done';
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9925-L9951
                                do_plot = false;
                                tauz = tau1 + (tau2-tau1)*rand(1,nsim);
                                samplez = samprate1+(samprate2-samprate1)*rand(1,nsim);
                                window_sim = window1 + (window2-window1) * rand(1,nsim);
                                y_grid = linspace(data(1,1),data(length(data(:,1)),1),nout);
                                y_grid = y_grid';
                                powy = zeros(nout,nsim);

                                for i=1:nsim
                                    window = window_sim(i);
                                    tau = tauz(i);
                                    interpolate_rate= samplez(i);
                                    
                                    % Fit a first‐order polynomial (linear trend)
                                    p = polyfit(data(:,1), data(:,2), 1);          % p(1) = slope, p(2) = intercept
                                    % If you want to replace the second column in `data` with the detrended series:
                                    data(:,2) = data(:,2) - polyval(p, data(:,1));
        
                                    [data_even] = interpolate(data,interpolate_rate);

                                    if padtype > 0
                                        data_even = zeropad2(data_even,window,padtype);
                                    end
                                    
                                    output = lyapunov_timeseries(data_even, tau, window, step_size, 0, do_plot);
                                    % interpolation
                                    powy(:,i)=interp1(output(:,1),output(:,2),y_grid);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9953-L9953
                                        disp(['Simulation step = ',num2str(i),' / ',num2str(nsim)]);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9963-L9963
                                end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9969-L9978
                                percent =[2.5,5,10,15.865,25,50,75,84.135,90,95,97.5];
                                npercent  = length(percent);
                                npercent2 = (length(percent)-1)/2;
                                powyp = prctile(powy, percent,2);
    
                                for i = 1: npercent
                                    powyadjustp1=powyp(:,i);
                                    powyad_p_nan(:,i) = powyadjustp1(~isnan(powyadjustp1));
                                end
                                y_grid_nan = y_grid(~isnan(powyp(:,1)));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L10026-L10026
                                data1 = [y_grid_nan,powyad_p_nan(:,npercent2+1)];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L10028-L10028
                                data2 = [y_grid_nan,powyad_p_nan];
%% End copied source
r = struct();
r.data1 = data1;
r.data2 = data2;
r.tauz = tauz;
r.samplez = samplez;
r.window_sim = window_sim;
r.y_grid = y_grid;
r.powyp = powyp;
r.y_grid_nan = y_grid_nan;
r.powyad_p_nan = powyad_p_nan;
r.percent = percent;
end

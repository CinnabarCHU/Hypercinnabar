function [retval, id] = analyzer(params, id)
% Lag1MonteCarlo.analyzer parameters: data nsim window1 window2 samprate1 samprate2 nout shiftwin.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5524
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lag1MonteCarlo-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
nsim = p.nsim;
window1 = p.window1;
window2 = p.window2;
samprate1 = p.samprate1;
samprate2 = p.samprate2;
nout = p.nout;
shiftwin = p.shiftwin;
if nsim < 50, error('Acycle:Lag1:Simulations','The GUIDE Monte Carlo callback requires at least 50 simulations.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5524-L5537
                            samplez = samprate1+(samprate2-samprate1)*rand(1,nsim);
                            window_sim = window1 + (window2-window1) * rand(1,nsim);
                            y_grid = linspace(data(1,1),data(length(data(:,1)),1),nout);
                            y_grid = y_grid';
                            powy = zeros(nout,nsim);
                            if shiftwin > 1
                                for i=1:nsim
                                    window = window_sim(i);
                                    interpolate_rate= samplez(i);
                                    [data_even] = interpolate(data,interpolate_rate);
                                    [rhox] = erhoAR1(data_even,window);
                                    y_grid_rand = -1*window/2 + window * rand(1);
                                    % interpolation
                                    powy(:,i)=interp1((rhox(:,1)+y_grid_rand),rhox(:,2),y_grid);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5550-L5558
                                end
                            elseif shiftwin == 1
                                for i=1:nsim
                                    window = window_sim(i);
                                    interpolate_rate= samplez(i);
                                    [data_even] = interpolate(data,interpolate_rate);
                                    [rhox] = erhoAR1(data_even,window);
                                    % interpolation
                                    powy(:,i)=interp1(rhox(:,1),rhox(:,2),y_grid);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5570-L5571
                                end
                            end  
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5577-L5586
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
r = struct();
r.samplez = samplez;
r.window_sim = window_sim;
r.y_grid = y_grid;
r.powy = powy;
r.percent = percent;
r.npercent = npercent;
r.npercent2 = npercent2;
r.powyp = powyp;
r.powyad_p_nan = powyad_p_nan;
r.y_grid_nan = y_grid_nan;
end

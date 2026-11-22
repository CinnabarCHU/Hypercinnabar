function [retval, id] = helper(params, id)
% LyapunovMonteCarlo.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9877
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LyapunovMonteCarlo-v1.0/helper', params, id, @execute);
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
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9877-L9891
                        if ndata > 1000
                            interpn = 1000;
                            step_size = round(datalength / 1000);
                        else
                            interpn = ndata;
                            step_size = 1;
                        end

                        if 0.3 * datalength > 400
                            window1 = 400;
                            window2 = 500;
                        else
                            window1 = .3 * datalength;
                            window2 = .4 * datalength;
                        end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9893-L9894
                        defaultans = {'1000',num2str(samp05), num2str(samp95), num2str(window1),num2str(window2),...
                            num2str(samp95),num2str(2*samp95),num2str(interpn),'0'};
%% End copied source
answer=defaultans;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9898-L9907
                            nsim = str2double(answer{1});
                            tau1 = min(str2double(answer{2}), str2double(answer{3}));
                            tau2 = max(str2double(answer{2}), str2double(answer{3}));
                            window1 = str2double(answer{4});
                            window2 = str2double(answer{5});
                            samprate1 = str2double(answer{6});
                            samprate2 = str2double(answer{7});
                            nout = str2double(answer{8});
                            shiftwin = 1;
                            padtype = str2double(answer{9});
%% End copied source
r = struct();
r.data = data;
r.nsim = nsim;
r.tau1 = tau1;
r.tau2 = tau2;
r.window1 = window1;
r.window2 = window2;
r.samprate1 = samprate1;
r.samprate2 = samprate2;
r.nout = nout;
r.step_size = step_size;
r.padtype = padtype;
r.unit=''; r.unit_type=0;
end

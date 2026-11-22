function [retval, id] = helper(params, id)
% Lag1MonteCarlo.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5392
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lag1MonteCarlo-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
samplerate=diff(data(:,1));
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5392-L5394
                    ndata = length(data(:,1));
                    datalength = data(length(data(:,1)),1)-data(1,1);
                    samp95 = prctile(samplerate,95);  % new version; 1-2 * sample 95% percentile
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5481-L5493
                        if ndata > 1000
                            interpn = 1000;
                        else
                            interpn = ndata;
                        end

                        if .3 * datalength > 400
                            window1 = 400;
                            window2 = 500;
                        else
                            window1 = .3 * datalength;
                            window2 = .4 * datalength;
                        end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5495-L5496
                        defaultans = {'1000',num2str(window1),num2str(window2),...
                            num2str(samp95),num2str(2*samp95),num2str(interpn),'15'};
%% End copied source
answer=defaultans;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5500-L5506
                            nsim = str2double(answer{1});
                            window1 = str2double(answer{2});
                            window2 = str2double(answer{3});
                            samprate1 = str2double(answer{4});
                            samprate2 = str2double(answer{5});
                            nout = str2double(answer{6});
                            shiftwin = str2double(answer{7});
%% End copied source
r = struct();
r.data = data;
r.nsim = nsim;
r.window1 = window1;
r.window2 = window2;
r.samprate1 = samprate1;
r.samprate2 = samprate2;
r.nout = nout;
r.shiftwin = shiftwin;
end

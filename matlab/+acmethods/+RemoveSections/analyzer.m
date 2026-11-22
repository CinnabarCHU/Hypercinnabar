function [retval, id] = analyzer(params, id)
% RemoveSections.analyzer parameters: dat sec.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L6256
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('RemoveSections-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
sec = p.sec;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6256-L6258
                dat = sortrows(dat);
                xmin = dat(1);
                xmax = dat(length(dat(:,1)));
%% End copied source
sec=reshape(sec,[],1); n_sec=numel(sec);
if n_sec==0 || mod(n_sec,2), error('Acycle:Sections:Pairs','Supply alternating locations and endpoints or durations.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6310-L6325
                        [data0] = select_interval(dat,xmin,sec(1));
                        data_mer = data0;
                        d_accum = 0;
                        for i = 1: n_sec/2
                            d = sec(2*i) - sec(2*i-1);
                            d_accum = d + d_accum;
                            if i == n_sec/2
                                [data1] = select_interval(dat,sec(2*i),xmax);
                                data1(:,1) = data1(:,1) - d_accum;
                                data_mer = [data_mer;data1];
                            else
                                [data2] = select_interval(dat,sec(2*i),sec(2*i+1));
                                data2(:,1) = data2(:,1) - d_accum;
                                data_mer = [data_mer;data2];
                            end    
                        end
%% End copied source
r = struct();
r.data_mer = data_mer;
end

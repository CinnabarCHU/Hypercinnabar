function [retval, id] = analyzer(params, id)
% MultiplySeries.analyzer parameters: series.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4732
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MultiplySeries-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
series = p.series;
if numel(series)~=2, error('Acycle:Multiply:Inputs','Expected two series.'); end
dat_new=series{1}; nplot=numel(series);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4732-L4734
    dat_new1 = dat_new;
    dat_new2 = dat_new;
    for i = 1:nplot
%% End copied source
data_filterout=series{i};
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4738-L4740
        dat_new1 = [dat_new(:,1),  dat_new1(:,2).* data_filterout(:,2)];
        dat_new2 = [data_filterout(:,1),  dat_new2(:,2).* data_filterout(:,2)];
    end
%% End copied source
r = struct();
r.dat_new1 = dat_new1;
r.dat_new2 = dat_new2;
end

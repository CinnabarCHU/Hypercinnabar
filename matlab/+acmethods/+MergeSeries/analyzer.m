function [retval, id] = analyzer(params, id)
% MergeSeries.analyzer parameters: series.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4681
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MergeSeries-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
series = p.series;
dat_new=series{1}; nplot=numel(series);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4681-L4681
    for i = 1:nplot
%% End copied source
data_filterout=series{i};
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4685-L4688
        dat_new = [dat_new; data_filterout];
        dat_merge = sortrows(dat_new);
    end
    dat_merge = findduplicate(dat_merge);
%% End copied source
r = struct();
r.dat_merge = dat_merge;
end

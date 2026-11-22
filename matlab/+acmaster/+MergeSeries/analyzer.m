function [retval,id] = analyzer(params,id)
% MergeSeries.analyzer parameters: series.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('MergeSeries-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
series = p.series;
dat_new=series{1}; nplot=numel(series);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L1514-L1514
    for i = 1:nplot
%% End copied source
data_filterout=series{i};
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5779-L5782
        dat_new = [dat_new; data_filterout];
        dat_merge = sortrows(dat_new);
    end
    dat_merge = findduplicate(dat_merge);
%% End copied source
r = struct();
r.dat_merge = dat_merge;
end

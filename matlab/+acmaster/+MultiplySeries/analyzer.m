function [retval,id] = analyzer(params,id)
% MultiplySeries.analyzer parameters: series.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('MultiplySeries-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
series = p.series;
if numel(series)~=2, error('Acycle:Multiply:Inputs','Expected two series.'); end
dat_new=series{1}; nplot=numel(series);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5826-L5828
    dat_new1 = dat_new;
    dat_new2 = dat_new;
    for i = 1:nplot
%% End copied source
data_filterout=series{i};
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5832-L5834
        dat_new1 = [dat_new(:,1),  dat_new1(:,2).* data_filterout(:,2)];
        dat_new2 = [data_filterout(:,1),  dat_new2(:,2).* data_filterout(:,2)];
    end
%% End copied source
r = struct();
r.dat_new1 = dat_new1;
r.dat_new2 = dat_new2;
end

function [retval,id] = analyzer(params,id)
% InterpolateSeries.analyzer parameters: dat1 dat2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/InterplationSeries.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('InterpolateSeries-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
dat1 = p.dat1; dat2 = p.dat2;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/InterplationSeries.m:L143-L150
                dat1 = sortrows(dat1,1);
                dat2 = sortrows(dat2,1);

                xmin = min([dat1(:,1); dat2(:,1)]);
                xmax = max([dat1(:,1); dat2(:,1)]);

                dat2int2 = interp1(dat2(:,1),dat2(:,2),dat1(:,1),'linear');
                dat2int = [dat1(:,1),dat2int2];
%% End copied source
r = struct();
r.dat1 = dat1;
r.dat2 = dat2;
r.dat2int = dat2int;
r.xmin = xmin;
r.xmax = xmax;
end

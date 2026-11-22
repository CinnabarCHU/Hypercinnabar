function [retval, id] = analyzer(params, id)
% InterpolateSeries.analyzer parameters: dat1 dat2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/InterplationSeries.m#L185
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('InterpolateSeries-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
dat1 = p.dat1;
dat2 = p.dat2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/InterplationSeries.m:L185-L189
xmin = min( min(dat1(:,1), min(dat2(:,1))));
xmax = max( max(dat1(:,1), max(dat2(:,1))));

dat2int2 = interp1(dat2(:,1),dat2(:,2),dat1(:,1));
dat2int  = [dat1(:,1),dat2int2];
%% End copied source
r = struct();
r.dat1 = dat1;
r.dat2 = dat2;
r.dat2int = dat2int;
r.xmin = xmin;
r.xmax = xmax;
end

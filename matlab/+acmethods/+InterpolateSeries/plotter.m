function [retval, id] = plotter(params, id)
% InterpolateSeries.plotter parameters: dat1 dat2 dat2int xmin xmax unit.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/InterplationSeries.m#L193
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('InterpolateSeries-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
dat1 = p.dat1;
dat2 = p.dat2;
dat2int = p.dat2int;
xmin = p.xmin;
xmax = p.xmax;
unit = p.unit;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/InterplationSeries.m:L193-L193
figure;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/InterplationSeries.m:L195-L198
subplot(3,1,1)

plot(dat1(:,1),dat1(:,2),'b--o')
xlim( [xmin, xmax] )
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/InterplationSeries.m:L200-L202
subplot(3,1,2)
plot(dat2(:,1),dat2(:,2),'r-s')
xlim( [xmin, xmax] )
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/InterplationSeries.m:L204-L206
subplot(3,1,3)
plot(dat2int(:,1),dat2int(:,2),'r-o')
xlim( [xmin, xmax] )
%% End copied source
xlabel(unit);
r=[];
end

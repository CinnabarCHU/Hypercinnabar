function [retval, id] = plotter(params, id)
% evopmtmML.plotter parameters: xgrid ratio pow powall dt fmin fmax window nw fterm filename.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/evopmtmML.m#L72
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('evopmtmML-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
xgrid = p.xgrid;
ratio = p.ratio;
pow = p.pow;
powall = p.powall;
dt = p.dt;
fmin = p.fmin;
fmax = p.fmax;
window = p.window;
nw = p.nw;
fterm = p.fterm;
filename = p.filename;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/evopmtmML.m:L72-L83
figure;
subplot(3,1,1);
plot(xgrid,ratio);
title(['pmtm ratio of selected frequency from ',num2str(fmin),' to ',num2str(fmax),char(10),...
       'Window, dt, nw and frequency cutoff are: ',num2str(window),', ' ,num2str(dt),', ',num2str(nw),', ', num2str(fterm)]);
subplot(3,1,2);
plot(xgrid,pow);
title(['Total power of selected frequency from ',num2str(fmin),' to ',num2str(fmax)])
subplot(3,1,3);
plot(xgrid,powall);
title(['Total power of frequency from 0 to ',num2str(fterm)])
set(gcf,'Name',[num2str(filename),': power ratio'])
%% End copied source
r=[];
end

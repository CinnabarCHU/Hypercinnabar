function [retval, id] = plotter(params, id)
% InterpolationPro.plotter parameters: data xq vq titlei legendi x1 x2 y1 y2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/update_interpolationGUI.m#L141
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('InterpolationPro-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
xq = p.xq;
vq = p.vq;
titlei = p.titlei;
legendi = p.legendi;
x1 = p.x1;
x2 = p.x2;
y1 = p.y1;
y2 = p.y2;
figure; handles.axes1=axes;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_interpolationGUI.m:L141-L149
plot(handles.axes1,data(:,1),data(:,2),'o')
hold on
plot(handles.axes1,xq,vq,':.')

title(titlei);
legend('raw',legendi)
xlim([x1, x2])
ylim([y1, y2])
hold off
%% End copied source
r=[];
end

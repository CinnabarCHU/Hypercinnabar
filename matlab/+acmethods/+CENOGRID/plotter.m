function [retval, id] = plotter(params, id)
% CENOGRID.plotter parameters: time value time2 value2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7971
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('CENOGRID-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
time = p.time;
value = p.value;
time2 = p.time2;
value2 = p.value2;
figure; dat_name='Example-cenogrid-d18o'; dat_name2='Example-cenogrid-d13c';
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7971-L7983
subplot(2,1,1)
plot(time,value)
xlim([0 67102])
% Flip the y-axis
axis ij;
% Set the axis properties
ax = gca;
ax.Color = 'white'; % Set background color to white
ax.TickDir = 'out'; % Set tick direction to outward
ax.XMinorTick = 'on'; % Turn on minor tick marks on the x-axis
ax.YMinorTick = 'on'; % Turn on minor tick marks on the y-axis
title(dat_name, 'Interpreter', 'none')
ylabel('CENOGRID d18O')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7985-L7985
    xlabel('Age (ka)')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7991-L8001
subplot(2,1,2)
plot(time2,value2)
xlim([0 67102])
% Set the axis properties
ax = gca;
ax.Color = 'white'; % Set background color to white
ax.TickDir = 'out'; % Set tick direction to outward
ax.XMinorTick = 'on'; % Turn on minor tick marks on the x-axis
ax.YMinorTick = 'on'; % Turn on minor tick marks on the y-axis
title(dat_name2, 'Interpreter', 'none')
ylabel('CENOGRID d13C')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8003-L8003
    xlabel('Age (ka)')
%% End copied source
r=[];
end

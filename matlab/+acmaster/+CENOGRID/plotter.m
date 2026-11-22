function [retval,id] = plotter(params,id)
% CENOGRID.plotter parameters: time value time2 value2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('CENOGRID-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
time = p.time;
value = p.value;
time2 = p.time2;
value2 = p.value2;
figure; dat_name='Example-cenogrid-d18o'; dat_name2='Example-cenogrid-d13c';
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8981-L8993
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
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8939-L8939
    xlabel('Age (ka)')
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L9001-L9011
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
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8939-L8939
    xlabel('Age (ka)')
%% End copied source
r=[];
end

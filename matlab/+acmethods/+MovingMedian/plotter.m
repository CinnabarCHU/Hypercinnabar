function [retval, id] = plotter(params, id)
% MovingMedian.plotter parameters: time value data dat_name ext.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7630
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MovingMedian-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
time = p.time;
value = p.value;
data = p.data;
dat_name = p.dat_name;
ext = p.ext;
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7630-L7633
                    plot(time,value,'k')
                    hold on;
                    plot(time,data(:,2),'r','LineWidth',2.5)
                    title([dat_name,ext], 'Interpreter', 'none')
%% End copied source
r=[];
end

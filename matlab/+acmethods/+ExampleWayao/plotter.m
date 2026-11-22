function [retval, id] = plotter(params, id)
% ExampleWayao.plotter parameters: data data_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8071
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleWayao-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
data_name = p.data_name;
[~,dat_name,ext]=fileparts(data_name);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8071-L8075
time = data(:,1);
value = data(:,2);
figure;
plot(time,value)
title([dat_name,ext], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8077-L8078
    xlabel('Depth (m)')
    ylabel('Gamma ray (cpm)')
%% End copied source
r=[];
end

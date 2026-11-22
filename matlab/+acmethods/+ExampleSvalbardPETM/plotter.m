function [retval, id] = plotter(params, id)
% ExampleSvalbardPETM.plotter parameters: data data_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7786
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleSvalbardPETM-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
data_name = p.data_name;
[~,dat_name,ext]=fileparts(data_name);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7786-L7790
time = data(:,1);
value = data(:,2);
figure;
plot(time,value)
title([dat_name,ext], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7792-L7792
    xlabel('Depth (m)')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7796-L7796
ylabel('Log(Fe)')
%% End copied source
r=[];
end

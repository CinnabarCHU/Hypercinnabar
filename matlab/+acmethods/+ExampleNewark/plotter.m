function [retval, id] = plotter(params, id)
% ExampleNewark.plotter parameters: data data_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8109
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleNewark-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
data_name = p.data_name;
[~,dat_name,ext]=fileparts(data_name);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8109-L8113
time = data(:,1);
value = data(:,2);
figure;
plot(time,value)
title([dat_name,ext], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8115-L8116
    xlabel('Depth (m)')
    ylabel('Depth Rank')
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% AstronomicalSolution.plotter parameters: dat solution parameter t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/basicseries.m#L451
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AstronomicalSolution-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
solution = p.solution;
parameter = p.parameter;
t1 = p.t1;
t2 = p.t2;
handles.solution=solution;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L451-L451
name = [handles.solution,'-',parameter,'-',num2str(t1),'-',num2str(t2),'.txt'];
%% End copied source
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L458-L458
plot(dat(:,1),dat(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L460-L460
xlim([min(dat(:,1)),max(dat(:,1))]);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L462-L462
    xlabel('Time (kyr)')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L469-L469
title(name, 'Interpreter', 'none')
%% End copied source
r=[];
end

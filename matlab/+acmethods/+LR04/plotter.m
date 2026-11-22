function [retval, id] = plotter(params, id)
% LR04.plotter parameters: LR04stack_s t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3061
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LR04-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
LR04stack_s = p.LR04stack_s;
t1 = p.t1;
t2 = p.t2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3061-L3062
    figure;
    plot(LR04stack_s(:,1),LR04stack_s(:,2),'LineWidth',1);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3064-L3066
        xlabel('Time (ka)')
        ylabel('Global Benthic \delta^{18}O')
        title(['LR04 Stack: ',num2str(t1),'_',num2str(t2),' ka'], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3072-L3072
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
r=[];
end

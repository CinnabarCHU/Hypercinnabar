function [retval,id] = plotter(params,id)
% LR04.plotter parameters: LR04stack_s t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('LR04-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
LR04stack_s = p.LR04stack_s;
t1 = p.t1;
t2 = p.t2;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4105-L4106
    figure;
    plot(LR04stack_s(:,1),LR04stack_s(:,2),'LineWidth',1);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4108-L4110
        xlabel('Time (ka)')
        ylabel('Global Benthic \delta^{18}O')
        title(['LR04 Stack: ',num2str(t1),'_',num2str(t2),' ka'], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L2706-L2706
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% PowerDecomposition.plotter parameters: pow.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L6184
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerDecomposition-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
pow = p.pow;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6184-L6186
            figure;
            plot(pow(:,1),pow(:,2),'k','LineWidth',1);
            set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6188-L6189
                xlabel('Time (kyr)')
                ylabel('Power ratio')
%% End copied source
r=[];
end

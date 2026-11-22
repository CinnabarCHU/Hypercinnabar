function [retval, id] = plotter(params, id)
% circularspec.plotter parameters: P R.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/circularspec.m#L78
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('circularspec-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
P = p.P;
R = p.R;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/circularspec.m:L78-L81
    figure;
    plot(P,R,'k-','LineWidth',2)
    xlabel('period')
    ylabel('power')
%% End copied source
r=[];
end

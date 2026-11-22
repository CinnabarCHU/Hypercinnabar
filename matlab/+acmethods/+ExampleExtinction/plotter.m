function [retval, id] = plotter(params, id)
% ExampleExtinction.plotter parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7851
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleExtinction-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7851-L7856
figure;
scatter(data,data,200,[0 0.4470 0.7410],'filled','MarkerFaceAlpha',0.5);
xlim([0 300])
ylim([0 300])
xlabel('Ma')
ylabel('Ma')
%% End copied source
r=[];
end

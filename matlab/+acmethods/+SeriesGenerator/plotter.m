function [retval, id] = plotter(params, id)
% SeriesGenerator.plotter parameters: x y.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/linegenerator.m#L242
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SeriesGenerator-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
x = p.x;
y = p.y;
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L242-L245
plot(x,y,'r-o')
xlim([min(x), max(x)])
xlabel('x')
ylabel('y')
%% End copied source
r=[];
end

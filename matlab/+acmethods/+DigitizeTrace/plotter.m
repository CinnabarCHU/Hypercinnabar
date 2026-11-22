function [retval, id] = plotter(params, id)
% DigitizeTrace.plotter parameters: image result.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DataExtractML.m#L811
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DigitizeTrace-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
I=p.image; [Ym,Yn,~]=size(I); figure; image(I); axis image; YYY=p.result.pixels;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DataExtractML.m:L812-L817
                hold on;
                plot(YYY(:,1),YYY(:,2),'ro')
                set(gca,'Ydir','reverse')
                xlim([1,Yn])
                ylim([1,Ym])
                hold off;
%% End copied source
r=[];
end

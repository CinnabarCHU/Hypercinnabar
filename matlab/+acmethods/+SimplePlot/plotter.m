function [retval, id] = plotter(params, id)
% SimplePlot.plotter parameters: series plot_list unit standardized offset.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3142
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SimplePlot-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
series = p.series;
plot_list = p.plot_list;
unit = p.unit;
standardized = p.standardized;
offset = p.offset;
figure; hold on;
for i=1:numel(series)
    dat=series{i};
    if standardized
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3142-L3143
            dat = dat(~any(isnan(dat),2),:);
            dat(:,2) = (dat(:,2)-mean(dat(:,2)))/std(dat(:,2));
%% End copied source
    end
    if offset
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3227-L3227
        plot(dat(:,1),dat(:,2) - 2*(i-1),'LineWidth',1);  % modify to fit with the order of title
%% End copied source
    else
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3144-L3144
            plot(dat(:,1),dat(:,2),'LineWidth',1);
%% End copied source
    end
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3146-L3147
    set(gca,'XMinorTick','on','YMinorTick','on')
    hold off
%% End copied source
title(plot_list,'Interpreter','none'); xlabel(unit);
r=[];
end

function [retval,id] = plotter(params,id)
% SimplePlot.plotter parameters: series plot_list unit standardized offset.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SimplePlot-v3.1.1+dcba427/plotter',params,id,@execute);
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
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4186-L4187
            dat = dat(~any(isnan(dat),2),:);
            dat(:,2) = (dat(:,2)-mean(dat(:,2)))/std(dat(:,2));
%% End copied source
    end
    if offset
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4273-L4273
        plot(dat(:,1),dat(:,2) - 2*(i-1),'LineWidth',1);  % modify to fit with the order of title
%% End copied source
    else
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4188-L4188
            plot(dat(:,1),dat(:,2),'LineWidth',1);
%% End copied source
    end
end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4190-L4191
    set(gca,'XMinorTick','on','YMinorTick','on')
    hold off
%% End copied source
title(plot_list,'Interpreter','none'); xlabel(unit);
r=[];
end

function [retval,id] = plotter(params,id)
% DYNOT.plotter parameters: data result.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/DYNOS.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DYNOT-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
S.data = p.data;
S.run = p.result;
fig = figure;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L821-L845
tiledlayout(fig,2,1,'Padding','compact','TileSpacing','compact');
nexttile;
plot(S.data(:,1),S.data(:,2),'Color',[0.2 0.6 1]);
title('Data');
grid on;
set(gca,'XMinorTick','on','YMinorTick','on');

nexttile;
ax = gca;
hold(ax,'on');
npercent = S.run.npercent;
npercent2 = S.run.npercent2;
y_grid_nan = S.run.y_grid_nan;
powyad_p_nan = S.run.powyad_p_nan;
colorcode = S.run.colorcode;
for i = 1:min(npercent2,size(colorcode,1))
    x = [y_grid_nan; flipud(y_grid_nan)];
    y = [powyad_p_nan(:,npercent+1-i); flipud(powyad_p_nan(:,i))];
    fill(ax,x,y,colorcode(i,:),'LineStyle','none');
end
medianIndex = S.run.medianIndex;
plot(ax,y_grid_nan,powyad_p_nan(:,medianIndex), ...
    'Color',[0 120/255 0],'LineWidth',1.5,'LineStyle','--');
set(ax,'YDir','reverse');
title(ax,'DYNOT');
%% End copied source
r = [];
end

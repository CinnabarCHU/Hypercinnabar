function [retval, id] = plotter(params, id)
% DYNOT.plotter parameters: y_grid_nan powyad_p_nan npercent npercent2 data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DYNOS.m#L754
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DYNOT-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
y_grid_nan = p.y_grid_nan;
powyad_p_nan = p.powyad_p_nan;
npercent = p.npercent;
npercent2 = p.npercent2;
data = p.data;
figure; handles.axes2=axes;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L754-L773
cla reset
hold all
% for i = 1: nmc
%     plot(y_grid,powyadjust(:,i),'color',[0,0,0]+0.8);
% end
%
colorcode = [221/255,234/255,224/255; ...
    201/255,227/255,209/255; ...
    176/255,219/255,188/255;...
    126/255,201/255,146/255;...
    67/255,180/255,100/255];
for i = 1:npercent2
    fill([y_grid_nan; (fliplr(y_grid_nan'))'],[powyad_p_nan(:,npercent+1-i);...
        (fliplr(powyad_p_nan(:,i)'))'],colorcode(i,:),'LineStyle','none');
end
plot(y_grid_nan,powyad_p_nan(:,npercent2+1),'Color',[0,120/255,0],'LineWidth',1.5,'LineStyle','--')
axis([data(1,1) data(length(data(:,1)),1) min(powyad_p_nan(:,npercent)) max(powyad_p_nan(:,1))]) 
set(handles.axes2,'Ydir','reverse')
set(gca,'XMinorTick','on','YMinorTick','on')
hold off
%% End copied source
r=[];
end

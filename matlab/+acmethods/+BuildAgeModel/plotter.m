function [retval, id] = plotter(params, id)
% BuildAgeModel.plotter parameters: agemodelfull sedrate period plot_filter_s unit.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3617
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('BuildAgeModel-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
agemodelfull = p.agemodelfull;
sedrate = p.sedrate;
period = p.period;
plot_filter_s = p.plot_filter_s;
unit = p.unit;
handles.unit=unit;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3617-L3621
                figure;
                set(gcf,'units','norm') % set location
                set(gcf,'position',[0.01,0.55,0.45,0.4]) % set position
                set(gcf,'color','w');
                plot(agemodelfull(:,1), agemodelfull(:,2),'k','LineWidth',1)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3623-L3626
                    set(gcf,'Name','Acycle: Build Age Model | Age Model','NumberTitle','off')
                    xlabel(['Depth (',handles.unit,')'])
                    ylabel('Time (kyr)')
                    title(['Age Model: ', num2str(period), ' kyr cycle: ', plot_filter_s])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3634-L3642
                set(gca,'XMinorTick','on','YMinorTick','on')
                xlim([agemodelfull(1,1), agemodelfull(end,1)])
                ylim([agemodelfull(1,2), agemodelfull(end,2)])
                
                figure;
                set(gcf,'color','w');
                set(gcf,'units','norm') % set location
                set(gcf,'position',[0.01,0.05,0.45,0.4]) % set position
                stairs(sedrate(:,1), sedrate(:,2),'k','LineWidth',1)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3644-L3647
                    set(gcf,'Name','Acycle: Build Age Model | Sedimentation Rate')
                    xlabel(['Depth (',handles.unit,')'])
                    ylabel(['Sedimentation rate (',handles.unit,'/kyr)'])
                    title(['Sedimentation rate: ', num2str(period), ' kyr cycle: ', plot_filter_s])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3654-L3656
                xlim([sedrate(1,1), sedrate(end,1)])
                ylim([0, max(sedrate(:,2)) * 2])
                set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
r=[];
end

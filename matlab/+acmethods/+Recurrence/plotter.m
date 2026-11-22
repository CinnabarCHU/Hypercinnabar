function [retval, id] = plotter(params, id)
% Recurrence.plotter parameters: t x S eps_plot DETx DETy showseries showdet fliptime flipseries ylabeli unit_type unit.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/update_recplot.m#L208
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Recurrence-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
t = p.t;
x = p.x;
S = p.S;
eps_plot = p.eps_plot;
DETx = p.DETx;
DETy = p.DETy;
showseries = p.showseries;
showdet = p.showdet;
fliptime = p.fliptime;
flipseries = p.flipseries;
ylabeli = p.ylabeli;
unit_type = p.unit_type;
unit = p.unit;
handles=struct('unit_type',unit_type,'unit',unit);
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L208-L210
set(gcf,'Color','w')
set(gcf,'Name','Recurrence Plot')
axis square;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L212-L343
if showseries == 1
    if showdet == 1
        % recurrence plot + series + DET
        subplot('position',[0.15 0.86 0.7 0.11]);
        plot(t,x,'k','LineWidth',1)
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        xlim([min(t), max(t)])
        ylabel(ylabeli)
        set(gca,'xticklabel',{[]})
        set(gca,'xdir', ternary(fliptime==1,'reverse','normal'));
        set(gca,'ydir', ternary(flipseries==1,'reverse','normal'));

        subplot('position',[0.15 0.75 0.7 0.11]);
        plot(DETx,DETy,'k','LineWidth',2)
        xlim([min(t), max(t)])
        ylim([0.9*min(DETy),1.1*max(DETy)])
        ylabel('DET')
        set(gca,'xticklabel',{[]})
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        set(gca,'xdir', ternary(fliptime==1,'reverse','normal'));

        subplot('position',[0.15 0.05 0.7 0.7]);
        imagesc(t, t, S < eps_plot);
        axis square;
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        colormap([1 1 1;0 0 0]);

        if handles.unit_type == 0
            xlabel(''); ylabel('');
        elseif handles.unit_type == 1
            xlabel(['Depth (',handles.unit,')'])
            ylabel(['Depth (',handles.unit,')'])
        else
            xlabel(['Time (',handles.unit,')'])
            ylabel(['Time (',handles.unit,')'])
        end

        if fliptime == 1
            set(gca,'xdir','reverse','ydir','reverse')
        else
            set(gca,'xdir','normal','ydir','normal')
        end

    else
        % recurrence plot + series
        subplot('position',[0.15 0.75 0.7 0.2]);
        plot(t,x,'k','LineWidth',1)
        xlim([min(t), max(t)])
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        ylabel(ylabeli)
        set(gca,'xticklabel',{[]})
        set(gca,'xdir', ternary(fliptime==1,'reverse','normal'));
        set(gca,'ydir', ternary(flipseries==1,'reverse','normal'));

        subplot('position',[0.15 0.05 0.7 0.7]);
        imagesc(t, t, S < eps_plot);
        axis square;
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        colormap([1 1 1;0 0 0]);

        if handles.unit_type == 0
            xlabel(''); ylabel('');
        elseif handles.unit_type == 1
            xlabel(['Depth (',handles.unit,')'])
            ylabel(['Depth (',handles.unit,')'])
        else
            xlabel(['Time (',handles.unit,')'])
            ylabel(['Time (',handles.unit,')'])
        end

        if fliptime == 1
            set(gca,'xdir','reverse','ydir','reverse')
        else
            set(gca,'xdir','normal','ydir','normal')
        end
    end
else
    if showdet == 1
        % recurrence plot + DET
        subplot('position',[0.15 0.75 0.7 0.2]);
        plot(DETx,DETy,'k','LineWidth',2)
        xlim([min(t), max(t)])
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        ylabel('DET')
        set(gca,'xticklabel',{[]})
        set(gca,'xdir', ternary(fliptime==1,'reverse','normal'));

        subplot('position',[0.15 0.05 0.7 0.7]);
        imagesc(t, t, S < eps_plot);
        axis square;
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
        colormap([1 1 1;0 0 0]);

        if handles.unit_type == 0
            xlabel(''); ylabel('');
        elseif handles.unit_type == 1
            xlabel(['Depth (',handles.unit,')'])
            ylabel(['Depth (',handles.unit,')'])
        else
            xlabel(['Time (',handles.unit,')'])
            ylabel(['Time (',handles.unit,')'])
        end

        if fliptime == 1
            set(gca,'xdir','reverse','ydir','reverse')
        else
            set(gca,'xdir','normal','ydir','normal')
        end
    else
        % recurrence plot only
        imagesc(t, t, S < eps_plot);
        axis square;
        colormap([1 1 1;0 0 0]);
        set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');

        if handles.unit_type == 0
            xlabel(''); ylabel('');
        elseif handles.unit_type == 1
            xlabel(['Depth (',handles.unit,')'])
            ylabel(['Depth (',handles.unit,')'])
        else
            xlabel(['Time (',handles.unit,')'])
            ylabel(['Time (',handles.unit,')'])
        end

        if fliptime == 1
            set(gca,'xdir','reverse','ydir','reverse')
        else
            set(gca,'xdir','normal','ydir','normal')
        end
    end
end
%% End copied source
r=[];
end

%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L364-L366
function out = ternary(cond, a, b)
if cond, out = a; else, out = b; end
end
%% End copied source

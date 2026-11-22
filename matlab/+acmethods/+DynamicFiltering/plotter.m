function [retval, id] = plotter(params, id)
% DynamicFiltering.plotter parameters: x_grid y_grid s unit window f_min f_max fc.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/dynamic_filter.m#L26
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DynamicFiltering-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
x_grid = p.x_grid;
y_grid = p.y_grid;
s = p.s;
unit = p.unit;
window = p.window;
f_min = p.f_min;
f_max = p.f_max;
fc = p.fc;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter.m:L26-L42
    evofftfig = figure;
    set(evofftfig,'units','norm') % set location
    set(evofftfig,'position',[0.05,0.4,0.9,0.55]) % set position
    set(evofftfig,'Name','Acycle: Dynamic Filtering | Frequency Stabilization') % set position
    
    pcolor(x_grid,y_grid,s)
    % adjust color and add basic annotations
    colormap(jet)
    set(gca,'TickDir','out')
    shading interp 
    str=sprintf('Window = %d %s',window,unit);
    title(str);
    xlabel(['Frequency (cycles/',unit,')']) 
    ylabel(['Depth (',unit,')'])
    %colorbar
    % EOF
    view([90 -90]); %used to swap the view at 90 degrees. 
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter.m:L108-L111
    figure(evofftfig)
    hold on
    plot(f_min,y_grid,'o-g')
    plot(f_max,y_grid,'o-g')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter.m:L124-L125
    plot(fc,y_grid,'-r')
    hold off
%% End copied source
r=[];
end

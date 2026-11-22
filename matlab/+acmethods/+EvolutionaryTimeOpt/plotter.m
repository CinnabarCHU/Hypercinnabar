function [retval, id] = plotter(params, id)
% EvolutionaryTimeOpt.plotter parameters: result window unit unit_type plot_2d flipy main_unit_selection lang_choice lang_id lang_var.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/eTimeOptGUI.m#L475
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EvolutionaryTimeOpt-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
q = p.result;
senv=q.senv; spow=q.spow; sopt=q.sopt;
x_grid=q.x_grid; y_grid=q.y_grid; window=p.window;
handles=p; lang_id=p.lang_id; lang_var=p.lang_var;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L451-L570
if handles.unit_type == 0
    y_grid = y_grid/100;
    window = window/100;  % use real window size
elseif handles.unit_type == 2
    
else
    if strcmp(handles.unit,'m')
        y_grid = y_grid/100;
        window = window/100;
    elseif strcmp(handles.unit,'dm')
        y_grid = y_grid/10;
        window = window/10;
    elseif strcmp(handles.unit,'mm')
        y_grid = y_grid*10;
        window = window*10;
    elseif strcmp(handles.unit,'km')
        y_grid = y_grid/100/1000;
        window = window/100/1000;
    elseif strcmp(handles.unit,'ft')
        y_grid = y_grid * 30.48/100;
        window = window* 30.48/100;
    end
end

eTimeOptfig = figure;
set(gcf,'color','w');
[~, main26] = ismember('main26',lang_id); % Sed. rate
[~, main34] = ismember('main34',lang_id); % Unit
[~, main23] = ismember('main23',lang_id); % Depth
[~, main21] = ismember('main21',lang_id); % Time
[~, topt18] = ismember('topt18',lang_id); %

subplot(1,3,1)
if handles.plot_2d == 1
    pcolor(x_grid,y_grid,senv)
    set(gca,'XMinorTick','on','YMinorTick','on')
    set(gca, 'TickDir', 'out')
else
    surf(x_grid,y_grid,senv)
    set(gca, 'TickDir', 'out')
end
colormap parula
shading interp
if or(handles.main_unit_selection == 0, handles.lang_choice == 0)
    xlabel('Sedimentation rate (cm/kyr)')
    title('r^2_e_n_v_e_l_o_p_e')
    if handles.unit_type == 0;
        ylabel(['Unit (',handles.unit,')'])
    elseif handles.unit_type == 1;
        ylabel(['Depth (',handles.unit,')'])
    else
        ylabel(['Time (',handles.unit,')'])
    end
else
    %%
    xlabel([lang_var{main26},' (cm/kyr)'])
    title('r^2_e_n_v_e_l_o_p_e')
    if handles.unit_type == 0
        ylabel([lang_var{main34},' (',handles.unit,')'])
    elseif handles.unit_type == 1
        ylabel([lang_var{main23},' (',handles.unit,')'])
    else
        ylabel([lang_var{main21},' (',handles.unit,')'])
    end
    
end

if handles.flipy == 1;
    set(gca,'Ydir','reverse')
end
colorbar('southoutside')
set(gca,'XMinorTick','on','YMinorTick','on')
set(gca,'TickDir','out');
subplot(1,3,2)
if handles.plot_2d == 1
    pcolor(x_grid,y_grid,spow)
    set(gca,'XMinorTick','on','YMinorTick','on')
    set(gca, 'TickDir', 'out')
else
    surf(x_grid,y_grid,spow)
    set(gca, 'TickDir', 'out')
end
colormap parula
shading interp
if or(handles.main_unit_selection == 0, handles.lang_choice == 0)
    xlabel('Sedimentation rate (cm/kyr)')
else
    xlabel([lang_var{main26},' (cm/kyr)'])
end
title('r^2_p_o_w_e_r')
if handles.flipy == 1;
    set(gca,'Ydir','reverse')
end
colorbar('southoutside')
set(gca,'XMinorTick','on','YMinorTick','on')
set(gca,'TickDir','out');
subplot(1,3,3)
if handles.plot_2d == 1
    pcolor(x_grid,y_grid,sopt)
    set(gca,'XMinorTick','on','YMinorTick','on')
    set(gca, 'TickDir', 'out')
else
    surf(x_grid,y_grid,sopt)
    set(gca, 'TickDir', 'out')
end
colormap parula
shading interp
if or(handles.main_unit_selection == 0, handles.lang_choice == 0)
    xlabel('Sedimentation rate (cm/kyr)')
else
    xlabel([lang_var{main26},' (cm/kyr)'])
end
title('r^2_o_p_t')
if handles.flipy == 1;
    set(gca,'Ydir','reverse')
end
%colorbar
colorbar('southoutside')
set(gca,'XMinorTick','on','YMinorTick','on')
set(gca,'TickDir','out');
%% End copied source
r=[];
end

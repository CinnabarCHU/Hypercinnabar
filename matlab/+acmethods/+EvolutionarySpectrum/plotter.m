function [retval, id] = plotter(params, id)
% EvolutionarySpectrum.plotter parameters: result data window step method freq_log MTMred plotseries fmin fmax unit filename plot_2d plot_log flipy rotate unit_type color colorgrid.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/evofftGUI.m#L355
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EvolutionarySpectrum-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
handles=p;
lang_var={'Power','Robust AR(1)','Median','Frequency','Unit','Depth','Time','Evolutionary Spectral Analysis','Window','Step'};
handles.lang_id={'spectral30','spectral06','main40','main14','main34','main23','main21','menu108','main41','main32'};
handles.lang_var=lang_var; handles.lang_choice=0; handles.main_unit_selection=0;
data=p.result.data; dataraw=p.data; s=p.result.s; x_grid=p.result.x_grid; y_grid=p.result.y_grid;
fmingrid=p.result.fmingrid;
window = p.window;
step = p.step;
method = p.method;
freq_log = p.freq_log;
MTMred = p.MTMred;
plotseries = p.plotseries;
fmin = p.fmin;
fmax = p.fmax;
unit = p.unit;
filename = p.filename;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L320-L320
[~,dat_name,ext] = fileparts(filename);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L355-L613
evofftfig = figure;
set(gcf,'Color', 'white')

[~, spectral30] = ismember('spectral30',handles.lang_id); % power
[~, spectral06] = ismember('spectral06',handles.lang_id); % Robust AR(1)
[~, main40] = ismember('main40',handles.lang_id); % median
[~, main14] = ismember('main14',handles.lang_id); % Frequency
[~, main34] = ismember('main34',handles.lang_id); % Unit
[~, main23] = ismember('main23',handles.lang_id); % Depth
[~, main21] = ismember('main21',handles.lang_id); % Time
[~, menu108] = ismember('menu108',handles.lang_id); % 
[~, main41] = ismember('main41',handles.lang_id); % Window
[~, main32] = ismember('main32',handles.lang_id); % Step

if handles.plot_2d == 1
    if and(MTMred == 1, plotseries ==0)
        % show MTM red noise, no data series is shown
        dt = median(diff(data(:,1)));
        nfft = length(data(:,1));
        [~, ~,~,redconfML96]=redconfML(data(:,2),dt,2,5*nfft,2,0.25,fmax,0);
        
        subplot(4,1,1)
        if handles.plot_log == 1
            % log power
            semilogy(redconfML96(:,1),redconfML96(:,2),'k')
            hold on;
            semilogy(redconfML96(:,1),redconfML96(:,3),'m-.');
            semilogy(redconfML96(:,1),redconfML96(:,5),'r--','LineWidth',2);
            semilogy(redconfML96(:,1),redconfML96(:,6),'b-.');
        else
            plot(redconfML96(:,1),redconfML96(:,2),'k')
            hold on; 
            plot(redconfML96(:,1),redconfML96(:,3),'m-.');
            plot(redconfML96(:,1),redconfML96(:,5),'r--','LineWidth',2);
            plot(redconfML96(:,1),redconfML96(:,6),'b-.');
            ylabel(lang_var{spectral30})
            legend(lang_var{spectral30},[lang_var{spectral06},' ',lang_var{main40}],...
            [lang_var{spectral06},' 95%'],[lang_var{spectral06},' 99%'])
        end
        xlim([fmin fmax])
        if freq_log == 1;
            xlim([fmingrid fmax])
            set(gca, 'XScale', 'log')
        end
        
        subplot(4,1,[2 3 4])
        if handles.plot_log == 0;
            pcolor(x_grid,y_grid,s)
        else
            s = log10(s);
            pcolor(x_grid(2:end),y_grid,s(:,2:end))
        end
        shading interp
        xlim([fmin fmax])
        set(gca,'XMinorTick','on','YMinorTick','on')
        xlabel([lang_var{main14},' (1/',unit,')'])
        set(gca,'TickDir','out');
        if handles.flipy == 1;
            set(gca,'Ydir','reverse')
        end
        if freq_log == 1;
            xlim([fmingrid fmax])
            set(gca, 'XScale', 'log')
        end
        
    elseif and(MTMred == 1, plotseries == 1)
        % working
        dt = median(diff(dataraw(:,1)));
        nfft = length(dataraw(:,1));
        [~, ~,~,redconfML96]=redconfML(data(:,2),dt,2,5*nfft,2,0.25,fmax,0);
        subplot(4,4,[2 3 4])
        if handles.plot_log == 1
            % log power
            semilogy(redconfML96(:,1),redconfML96(:,2),'k')
            hold on; 
            semilogy(redconfML96(:,1),redconfML96(:,3),'m-.');
            semilogy(redconfML96(:,1),redconfML96(:,5),'r--','LineWidth',2);
            semilogy(redconfML96(:,1),redconfML96(:,6),'b-.');
        elseif handles.plot_log == 0
            plot(redconfML96(:,1),redconfML96(:,2),'k')
            hold on; 
            plot(redconfML96(:,1),redconfML96(:,3),'m-.');
            plot(redconfML96(:,1),redconfML96(:,5),'r--','LineWidth',2);
            plot(redconfML96(:,1),redconfML96(:,6),'b-.');
            ylabel(lang_var{spectral30})
            legend(lang_var{spectral30},[lang_var{spectral06},' ',lang_var{main40}],...
            [lang_var{spectral06},' 95%'],[lang_var{spectral06},' 99%'])
        end
        xlim([fmin fmax])
        if freq_log == 1;
            xlim([fmingrid fmax])
            set(gca, 'XScale', 'log')
        end
        
        subplot(4,4,[5 9 13])
        plot(dataraw(:,2),dataraw(:,1), 'k')
        ylim([dataraw(1,1) dataraw(end,1)])
        xlim([min(dataraw(:,2)) max(dataraw(:,2))])
        if handles.flipy == 1;
            set(gca,'Ydir','reverse')
        end
        
        if or(handles.lang_choice == 0, handles.main_unit_selection == 0)
            if handles.unit_type == 0
                ylabel(['Unit (',handles.unit,')'])
            elseif handles.unit_type == 1
                ylabel(['Depth (',handles.unit,')'])
            else
                ylabel(['Time (',handles.unit,')'])
            end
        else
            if handles.unit_type == 0
                ylabel([lang_var{main34},' (',handles.unit,')'])
            elseif handles.unit_type == 1
                ylabel([lang_var{main23},' (',handles.unit,')'])
            else
                ylabel([lang_var{main21},' (',handles.unit,')'])
            end
        end
        
        subplot(4,4,[6,7,8,10,11,12,14,15,16])
        
        if handles.plot_log == 0;
            pcolor(x_grid,y_grid,s)
        else
            s = log10(s);
            pcolor(x_grid,y_grid,s)
            %pcolor(x_grid(2:end),y_grid,s(:,2:end))
        end
        shading interp
        ylim([dataraw(1,1) dataraw(end,1)])
        xlim([fmin fmax])
        xlabel([lang_var{main14},' (1/',unit,')'])
        if handles.flipy == 1;
            set(gca,'Ydir','reverse')
        end
        if freq_log == 1;
            xlim([fmingrid fmax])
            set(gca, 'XScale', 'log')
        end
        set(gca,'TickDir','out');
        set(gca,'XMinorTick','on','YMinorTick','on')
    elseif and(MTMred == 0, plotseries == 1)
        % done...
        subplot(1,4,1)
        plot(dataraw(:,2),dataraw(:,1), 'k')
        ylim([dataraw(1,1) dataraw(end,1)])
        xlim([min(dataraw(:,2)) max(dataraw(:,2))])
        if handles.flipy == 1;
            set(gca,'Ydir','reverse')
        end
        
        if or(handles.lang_choice == 0, handles.main_unit_selection == 0)
            if handles.unit_type == 0
                ylabel(['Unit (',handles.unit,')'])
            elseif handles.unit_type == 1
                ylabel(['Depth (',handles.unit,')'])
            else
                ylabel(['Time (',handles.unit,')'])
            end
        else
            if handles.unit_type == 0
                ylabel([lang_var{main34},' (',handles.unit,')'])
            elseif handles.unit_type == 1
                ylabel([lang_var{main23},' (',handles.unit,')'])
            else
                ylabel([lang_var{main21},' (',handles.unit,')'])
            end
        end

        subplot(1,4,[2 3 4])
        if handles.plot_log == 0;
            pcolor(x_grid,y_grid,s)
        else
            s = log10(s);
            pcolor(x_grid(2:end),y_grid,s(:,2:end))
        end
        shading interp
        xlabel([lang_var{main14},' (1/',unit,')'])
        xlim([fmin fmax])
        ylim([dataraw(1,1) dataraw(end,1)])
        if handles.flipy == 1;
            set(gca,'Ydir','reverse')
        end
        if freq_log == 1;
            xlim([fmingrid fmax])
            set(gca, 'XScale', 'log')
        end
        set(gca,'XMinorTick','on','YMinorTick','on')
        set(gca,'TickDir','out');
    elseif and(MTMred == 0, plotseries == 0)
        % done
        if handles.plot_log == 0;
            pcolor(x_grid,y_grid,s)
        else
            s = log10(s);
            pcolor(x_grid(2:end),y_grid,s(:,2:end))
        end
        shading interp
        xlabel([lang_var{main14},' (1/',unit,')'])
        xlim([fmin fmax])
        set(gca,'XMinorTick','on','YMinorTick','on')
        if handles.flipy == 1;
            set(gca,'Ydir','reverse')
        end
        if freq_log == 1;
            xlim([fmingrid fmax])
            set(gca, 'XScale', 'log')
        end
        set(gca,'TickDir','out');
    end
    
    if plotseries == 0
        if or(handles.lang_choice == 0, handles.main_unit_selection == 0)
            if handles.unit_type == 0
                ylabel(['Unit (',handles.unit,')'])
            elseif handles.unit_type == 1
                ylabel(['Depth (',handles.unit,')'])
            else
                ylabel(['Time (',handles.unit,')'])
            end
        else
            if handles.unit_type == 0
                ylabel([lang_var{main34},' (',handles.unit,')'])
            elseif handles.unit_type == 1
                ylabel([lang_var{main23},' (',handles.unit,')'])
            else
                ylabel([lang_var{main21},' (',handles.unit,')'])
            end
        end
    else
        if MTMred == 0
            subplot(1,4,[2 3 4])
            set(gca,'YTickLabel',[]);
        else
            subplot(4,4,[6,7,8,10,11,12,14,15,16])
            set(gca,'YTickLabel',[]);
        end
    end
    
    % set
    if MTMred == 0
        title([method,'; ',lang_var{main41},' = ',num2str(window),' ',unit,'; ',lang_var{main32},' = ',num2str(step),' ', unit])
    else
        if plotseries == 0
            subplot(4,1,1)
            title([method,'; ',lang_var{main41},' = ',num2str(window),' ',unit,'; ',lang_var{main32},' = ',num2str(step),' ', unit])
        else
            subplot(4,4,[2 3 4])
            title([method,'; ',lang_var{main41},' = ',num2str(window),' ',unit,'; ',lang_var{main32},' = ',num2str(step),' ', unit])
        end
        set(gca,'XTickLabel',[]);
    end

    
else
    % 3D
    if handles.plot_log == 1;
        s = log10(s); 
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L615-L616
        surf(x_grid(2:end),y_grid,s(:,2:end))
    else
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L618-L662
        surf(x_grid,y_grid,s)
    end
    shading interp
    set(gca,'TickDir','out');
    set(gca,'XMinorTick','on','YMinorTick','on')
    xlabel([lang_var{main14},' (1/',unit,')'])
    xlim([fmin fmax])
    if handles.flipy == 1
        set(gca,'Ydir','reverse')
    end
    if freq_log == 1
        xlim([fmingrid fmax])
        set(gca, 'XScale', 'log')
    end
end

%colormap(jet)
if isempty(handles.colorgrid)
    % no grid
    setcolor = handles.color;
else
    setcolor = [handles.color,'(',round(num2str(handles.colorgrid)),')'];
end

try colormap(setcolor)
catch
    colormap default
end

shading interp
set(gcf,'Name',[dat_name,ext,': ',lang_var{menu108}])
set(gca,'XMinorTick','on','YMinorTick','on')
if handles.plot_2d == 1
    set(gca, 'TickDir', 'out')
else
   set(gca, 'TickDir', 'out')
   if handles.rotate == 0
        view(10,70);
    else
        for i = 1: 370
            view(i,70); 
            pause(0.05); 
        end
   end
end
%% End copied source
r=[];
end

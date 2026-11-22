function [retval,id] = plotter(params,id)
% recplot.plotter parameters: plotn S threshold t x labelx labely.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/recurrence/recplot.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('recplot-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
plotn = p.plotn;
S = p.S;
threshold = p.threshold;
t = p.t;
x = p.x;
labelx = p.labelx;
labely = p.labely;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/recurrence/recplot.m:L45-L56
if plotn == 1
    figure;
    set (gcf,'color','w','Name','Recurrence Plot')
    % imagesc(t, t, S < 0.2);
    rep = imagesc(t, t, S < threshold);
    
    axis square; 
    colormap([1 1 1;0 0 0]); 
    xlabel(labelx), 
    ylabel(labelx)
    %set (gca, 'xdir', 'reverse' )
    ylabel(labelx)
%% End copied source
set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/recurrence/recplot.m:L59-L80
elseif plotn == 2
    
    figure;
    set (gcf,'color','w','Name','Recurrence Plot')
    % R2019a
    try
        % Requires R2019b or later
        paneli = tiledlayout(2,1,'TileSpacing','Compact','Padding','Compact');
        nexttile
        plot(t,x)
        xlim([min(t), max(t)])
        axis square; 
        xlabel(labelx)
        ylabel(labely)
        %set (gca, 'xdir', 'reverse' )
        
        nexttile
        imagesc(t, t, S < threshold);
        axis square; 
        colormap([1 1 1;0 0 0]); 
        xlabel(labelx)
        ylabel(labelx)
%% End copied source
set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/recurrence/recplot.m:L84-L89
    catch
        subplot(2,1,1)
        plot(t,x)
        xlim([min(t), max(t)])
        axis square; 
        ylabel(labely)
%% End copied source
set(gca,'TickDir','out');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/recurrence/recplot.m:L93-L99
        subplot(2,1,2)
        
        imagesc(t, t, S < threshold);
        axis square; 
        colormap([1 1 1;0 0 0]); 
        xlabel(labelx)
        ylabel(labelx)
%% End copied source
set(gca,'XMinorTick','on','YMinorTick','on','TickDir','out');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/recurrence/recplot.m:L103-L104
    end
end
%% End copied source
r=[];
end

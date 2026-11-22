function [retval,id] = plotter(params,id)
% EvolutionarySpectrum.plotter parameters: result dimension logPower logFrequency reverseY fmin fmax unit.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/evofftGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EvolutionarySpectrum-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
v=p.result; s=v.s; x_grid=v.x_grid; y_grid=v.y_grid; app.plot_log=p.logPower;
fmin=p.fmin; fmax=p.fmax; l_freq='Frequency'; unit=p.unit;
figure;
if p.dimension==2
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/evofftGUI.m:L785-L792
                    if app.plot_log == 0
                        pcolor(x_grid,y_grid,s);
                    else
                        pcolor(x_grid(2:end),y_grid,log10(s(:,2:end)));
                    end
                    shading interp;
                    xlim([fmin fmax]);
                    xlabel([l_freq,' (1/',unit,')']);
%% End copied source
elseif p.dimension==3
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/evofftGUI.m:L902-L910
                if app.plot_log == 1
                    surf(x_grid(2:end),y_grid,log10(s(:,2:end)));
                else
                    surf(x_grid,y_grid,s);
                end
                ax3d = gca;
                shading interp;
                xlabel([l_freq,' (1/',unit,')']);
                xlim([fmin fmax]);
%% End copied source
    view(ax3d,10,70);
else, error('Acycle:Evo:Dimension','Choose 2 or 3 dimensions.'); end
if p.logFrequency
    positive=x_grid(isfinite(x_grid) & x_grid>0); lo=max(fmin,min(positive));
    xlim([lo,fmax]); set(gca,'XScale','log');
end
if p.reverseY, set(gca,'YDir','reverse'); end
r=[];
end

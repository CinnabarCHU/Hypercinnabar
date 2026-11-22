function [retval,id] = plotter(params,id)
% SWA.plotter parameters: freq power swa clfdr chi2_inv_value freqb pow2 bayesprob curves figure_count log_y log_x period_axis fmin fmax unit filename.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/SWAgui.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SWA-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
freq = p.freq;
power = p.power;
swa = p.swa;
clfdr = p.clfdr;
chi2_inv_value = p.chi2_inv_value;
freqb = p.freqb;
pow2 = p.pow2;
bayesprob = p.bayesprob;
curves = p.curves;
figure_count = p.figure_count;
log_y = p.log_y;
log_x = p.log_x;
period_axis = p.period_axis;
fmin = p.fmin;
fmax = p.fmax;
unit = p.unit;
filename = p.filename;
[~,fName,ext]=fileparts(filename);
handles=struct('unit',unit);
checkbox1x=struct('Value',num2cell(logical(curves)));
checkbox3x=struct('Value',num2cell((1:3)==figure_count));
checkbox21.Value=~log_y; checkbox22.Value=log_y; checkbox23.Value=log_x; checkbox24.Value=period_axis;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/SWAgui.m:L219-L221
    xvalue = freq;
    xvalueb = freqb;  %
    xlabel1 = ['Frequency (cycles/',handles.unit,')'];
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/SWAgui.m:L224-L232
    if checkbox24.Value == 1  % x in period
        xvalue = 1./freq;
        xlabel1 = ['Period (',handles.unit,')'];
        xvalueb = 1./freqb;
        pmin = 1/fmax;
        pmax = 1/fmin;
        fmax = pmax;
        fmin = pmin;
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/SWAgui.m:L235-L372
        figHandle = findobj('Type', 'figure', 'Name', ['Acycle: SWA - ', fName, ext]);
        if isempty(figHandle)
            figHandle = figure('Name', ['Acycle: SWA - ', fName, ext]);
        else
            clf(figHandle);  % Clear figure content
            figure(figHandle); % Bring to focus
        end

        if checkbox3x(1).Value   % all in one figure
            subplot(3,1,1)
        end
        hold on
        %% plot FDR
        if checkbox1x(8).Value  % 0.01% FDR
            plot(xvalue, clfdr(:,5),'k--','LineWidth',0.5,'DisplayName','0.01% FDR');
        end
        if checkbox1x(7).Value  % 0.1% FDR
            plot(xvalue, clfdr(:,4),'g--','LineWidth',0.5,'DisplayName','0.1% FDR'); % 0.1% FDR
        end
        if checkbox1x(6).Value  % 1% FDR
            plot(xvalue, clfdr(:,3),'b--','LineWidth',0.5,'DisplayName','1% FDR'); % 1% FDR
        end
        if checkbox1x(5).Value  % 5% FDR
            plot(xvalue, clfdr(:,2),'r-.','LineWidth',2,'DisplayName','5% FDR'); % 5% FDR
        end

        if checkbox1x(4).Value  % 99.9% chi2 CL
            plot(xvalue, swa * chi2_inv_value(4),'m-.','LineWidth',0.5,'DisplayName','99.9% chi^2 CL'); % 99.9%
        end
        if checkbox1x(3).Value  % 99% chi2 CL
            plot(xvalue, swa * chi2_inv_value(3),'b-.','LineWidth',0.5,'DisplayName','99% chi^2 CL'); % 99%
        end
        if checkbox1x(2).Value  % 95% chi2 CL
            plot(xvalue, swa * chi2_inv_value(2),'r--','LineWidth',1.5,'DisplayName','95% chi^2 CL'); % 95%
        end
        if checkbox1x(1).Value  % 90% chi2 CL
            plot(xvalue, swa * chi2_inv_value(1),'r-','LineWidth',0.5,'DisplayName','90% chi^2 CL'); % 90%
        end
        plot(xvalue, swa,'k-','LineWidth',2,'DisplayName','Background'); % SWA
        plot(xvalue, power,'k-','LineWidth',0.5,'DisplayName','Power'); % real power
        ylabel('Power')
        title('Lomb-Scargle Transform and SWA Confidence Levels')

        if checkbox21.Value  % linear Y
            set(gca,'YScale','linear');
        end
        if checkbox22.Value  % log Y
            set(gca,'YScale','log');
        end
        if checkbox23.Value  % linear Y
            set(gca,'XScale','log');
        else
            set(gca,'XScale','linear');
        end
        if checkbox24.Value == 1
            set(gca,'XDir','reverse')
        end
        xlabel(xlabel1)
        xlim([fmin, fmax])
        set(gca,'XMinorTick','on','YMinorTick','on')
        set(gcf,'Color', 'white')
        legend

        %% SWA
        if checkbox3x(1).Value  % All in 1 figure
            subplot(3,1,2)
        else 
            figHandle2 = findobj('Type', 'figure', 'Name', ['Acycle: SWA Periodogram - ', fName, ext]);
            if isempty(figHandle2)
                figHandle2 = figure('Name', ['Acycle: SWA Periodogram - ', fName, ext]);
            else
                clf(figHandle2);  % Clear figure content
                figure(figHandle2); % Bring to focus
            end
            if checkbox3x(2).Value % in two figures
                subplot(2,1,1)
            end
        end
        plot(xvalueb, pow2,'k-','DisplayName','Power')
        ylabel('Power')

        if checkbox21.Value  % linear Y
            set(gca,'YScale','linear');
        end
        if checkbox22.Value  % log Y
            set(gca,'YScale','log');
        end
        if checkbox23.Value  % linear Y
            set(gca,'XScale','log');
        else
            set(gca,'XScale','linear');
        end
        if checkbox24.Value == 1
            set(gca,'XDir','reverse')
        end
        xlabel(xlabel1)
        xlim([fmin, fmax])
        set(gca,'XMinorTick','on','YMinorTick','on')
        set(gcf,'Color', 'white')
        %% Bayesian Probability
        if checkbox3x(1).Value % All in 1 figure
            subplot(3,1,3)
        else
            if checkbox3x(2).Value % in two figures
                subplot(2,1,2)
            else  % in three figures
                figHandle3 = findobj('Type', 'figure', 'Name', ['Acycle: SWA Bayesian Probability - ', fName, ext]);
                if isempty(figHandle3)
                    figHandle3 = figure('Name', ['Acycle: SWA Bayesian Probability - ', fName, ext]);
                else
                    clf(figHandle3);  % Clear figure content
                    figure(figHandle3); % Bring to focus
                end
            end
        end
        plot(xvalueb, bayesprob,'k-','DisplayName','Bayesian Probability')
        ylabel('Bayesian probability')
        ylim([min(bayesprob), 1.1])

        if checkbox21.Value  % linear Y
            set(gca,'YScale','linear');
        end
        if checkbox22.Value  % log Y
            set(gca,'YScale','log');
        end
        if checkbox23.Value  % linear Y
            set(gca,'XScale','log');
        else
            set(gca,'XScale','linear');
        end
        if checkbox24.Value == 1
            set(gca,'XDir','reverse')
        end
        xlabel(xlabel1)
        xlim([fmin, fmax])
        set(gca,'XMinorTick','on','YMinorTick','on')
        set(gcf,'Color', 'white')
        hold off
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% CircularSpectrum.plotter parameters: result flipx unit.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/circularspecGUI.m#L377
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('CircularSpectrum-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
flipx = p.flipx;
unit = p.unit;
handles.unit = unit;
v=p.result; P=v.P; R=v.R; p1=v.p1; p2=v.p2; pn=v.pn; clmodel=v.clmodel;
if clmodel<3, Y=v.Y; cl=v.cl; end
if clmodel==2, theowhite=v.theowhite; pll=v.pll; end
if clmodel>=2, chi90=v.chi90; chi95=v.chi95; chi99=v.chi99; chi999=v.chi999; end
if clmodel==3, theored1=v.theored1; pxxsmooth=v.pxxsmooth; nw2=v.nw2; smoothwin=v.smoothwin; end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/circularspecGUI.m:L377-L482
    if clmodel < 3
        % fixed OR random with monte carlo
        figure;
        set(gcf,'Color', 'white')
        subplot(2,1,1)
        xlabel(['Period (',handles.unit,')'])
        ylabel('Power')
        hold on;
        plot(P,Y(4,:),'g-','LineWidth',1)
        plot(P,Y(3,:),'r-','LineWidth',3)
        plot(P,Y(2,:),'b-','LineWidth',1)
        plot(P,Y(1,:),'k-','LineWidth',1)
        plot(P,R,'LineWidth',1,'color',[0.9290, 0.6940, 0.1250])
        hold off
        if clmodel == 1
            title('CSA with Confidence Levels (Monte Carlo, fixed distance)')
        elseif clmodel == 2
            title('CSA with Confidence Levels (Monte Carlo, random distance)')
        end
        xlim([p1,p2])
        legend('99%','95%','90%','50%','power')
        if flipx; set(gca, 'XDir','reverse'); end

        subplot(2,1,2)
        hold on
        plot(P,ones(1,pn)*95,'r-','LineWidth',3)
        plot(P,ones(1,pn)*99,'g-','LineWidth',1)
        plot(P,cl*100,'LineWidth',1,'color',[0.9290, 0.6940, 0.1250])
        hold off
        ylim([90,100])
        xlabel(['Period (',handles.unit,')'])
        ylabel('Confidence level (%)')
        xlim([p1,p2])
        if flipx; set(gca, 'XDir','reverse'); end
        
        % random with theoretic
        if clmodel == 2
            figure;
            set(gcf,'Color', 'white')
            subplot(2,1,1)
            hold on;
            plot(P,chi99,'g-','LineWidth',1)
            plot(P,chi95,'r-','LineWidth',3)
            plot(P,chi90,'b-','LineWidth',1)
            plot(P,theowhite,'k-','LineWidth',1)
            plot(P,R,'LineWidth',1,'color',[0.9290, 0.6940, 0.1250]);
            title('CSA with Confidence Levels (white, chi2, random distance)')
            xlabel(['Period (',handles.unit,')'])
            ylabel('Power')
            xlim([p1,p2])
            legend('99%','95%','90%','50%','power')
            if flipx; set(gca, 'XDir','reverse'); end

            subplot(2,1,2)
            hold on
            plot(P,ones(1,pn)*95,'r-','LineWidth',3)
            plot(P,ones(1,pn)*99,'g-','LineWidth',1)
            plot(P,pll*100,'LineWidth',1,'color',[0.9290, 0.6940, 0.1250])
            hold off
            ylim([90,100])
            xlabel(['Period (',handles.unit,')'])
            ylabel('Confidence level (%)')
            xlim([p1,p2])
            if flipx; set(gca, 'XDir','reverse'); end
        end
    
    elseif clmodel == 3
        
        figure; 
        set(gcf,'Color', 'white')
        subplot(2,1,1)
        hold on; 
        semilogy(P,chi999,'g--','LineWidth',1);
        semilogy(P,chi99,'b-.');
        semilogy(P,chi95,'r--','LineWidth',2);
        semilogy(P,chi90,'r-');
        semilogy(P,theored1,'k-','LineWidth',2);
        semilogy(P,pxxsmooth,'m-.');
        semilogy(P,R,'k')
        xlim([p1,p2])
        xlabel(['Period (',handles.unit,')'])
        ylabel('Power')
        title('CSA with Confidence Levels (red, chi2, random distance)')
        smthwin = [num2str(smoothwin*100),'%', ' median-smoothed'];
        legend('Robust AR(1) 99.9%', 'Robust AR(1) 99%', 'Robust AR(1) 95%','Robust AR(1) 90%',...
            'Robust AR(1) median',smthwin,'Power')
        if flipx; set(gca, 'XDir','reverse'); end
        
        subplot(2,1,2)
        hold on
        chi2norm = R./theored1';
        chi2normnw2 = chi2norm' * nw2;
        pl = chi2cdf(chi2normnw2,nw2);
        
        plot(P,ones(1,pn)*90,'r-.','LineWidth',1)
        plot(P,ones(1,pn)*95,'r--','LineWidth',3)
        plot(P,ones(1,pn)*99,'b-.','LineWidth',1)
        plot(P,ones(1,pn)*99.9,'g--','LineWidth',1)
        plot(P,pl*100,'LineWidth',1,'color',[0.9290, 0.6940, 0.1250])
        xlim([p1,p2])
        hold off
        ylim([80,100])
        xlabel(['Period (',handles.unit,')'])
        ylabel('confidence level (%)')
        if flipx; set(gca, 'XDir','reverse'); end
    end
%% End copied source
r=[];
end

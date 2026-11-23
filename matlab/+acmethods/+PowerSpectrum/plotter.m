function [retval, id] = plotter(params, id)
% PowerSpectrum.plotter parameters: fd1 po fmin fmax unit plot_x_period linlogY logfreq.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L604
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerSpectrum-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
if isfield(p,'result')
    fd1=p.result.fd1; po=p.result.po;
else
    fd1=p.fd1; po=p.po;
end
fmin = p.fmin;
fmax = p.fmax;
unit = p.unit;
plot_x_period = p.plot_x_period;
linlogY = p.linlogY;
logfreq = p.logfreq;
handles=struct('linlogY',linlogY,'logfreq',logfreq); pt=1./fd1; figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L604-L607
        set(gcf,'Color', 'white')
        if plot_x_period
            pt1 = 1./fd1;
            plot(pt1(2:end),po(2:end),'k-','LineWidth',1);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L609-L609
                xlabel(['Period (',num2str(unit),')']) 
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L614-L621
            if fmin <= 0 
                fmin_s = pt(3);
            else
                fmin_s = 1/fmin;
            end

            xlim([1/fmax, fmin_s]);
            set(gca, 'XDir','reverse')
%% End copied source
else
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L631-L632
            plot(fd1(2:end),po(2:end),'k-','LineWidth',1);
            xlim([fmin fmax]);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L634-L634
                xlabel(['Frequency (cycles/',num2str(unit),')']) 
%% End copied source
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L651-L651
            ylabel('Power')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L675-L682
        if handles.linlogY == 1
            set(gca, 'YScale', 'log')
        else
            set(gca, 'YScale', 'linear')
        end
        if handles.logfreq == 1
            set(gca,'xscale','log')
        end
%% End copied source
if isfield(p,'result') && isfield(p.result,'models')
    renderModels(p,p.result);
end
r=[];
end

function renderModels(p,q)
m=q.models; handles=p; handles.lang_choice=0; handles.main_unit_selection=0; handles.lang_id={}; handles.lang_var={};
unit=p.unit; fmin=p.fmin; fmax=p.fmax; nw=p.nw; dt=q.dt; smoothwin=p.noise.smoothwin;
fd1=q.fd1; po=q.po; method=p.method; plot_x_period=p.plot_x_period;
bw=nw/(p.data(end,1)-p.data(1,1)); dat_name=''; ext=''; 
if isfield(m,'classic')
    c=m.classic; theored=c.theored;
    if strcmp(method,'Multi-taper method')
        fd=c.fd; po=c.po; rho=c.rho; tabtchi90=c.tabtchi90; tabtchi95=c.tabtchi95; tabtchi99=c.tabtchi99; tabtchi999=c.tabtchi999;
        if plot_x_period
            figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L85-L102
    pt = 1./fd;
    plot(pt,po,'k-','LineWidth',1);
    hold on; 
    plot(pt,theored,'k-','LineWidth',2);
    plot(pt,tabtchi90,'r-','LineWidth',1);
    plot(pt,tabtchi95,'r--','LineWidth',2);
    plot(pt,tabtchi99,'b-.','LineWidth',1);
    plot(pt,tabtchi999,'g--','LineWidth',1);
    
    if fmin <= 0 
        fmin_s = pt(3);
    else
        fmin_s = 1/fmin;
    end
    
    xlim([1/fmax, fmin_s]);
    set(gca, 'XDir','reverse')
    
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L104-L107
        xlabel(['Period (',num2str(unit),')']) 
        ylabel('Power')
        title([num2str(nw),'\pi MTM classic AR1',' ','; Sampling rate = ',num2str(dt),' ', unit])
        legend('Power','AR1','90%','95%','99%','99.9%')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L118-L127
        
    
    if handles.linlogY == 1
        set(gca, 'YScale', 'log')
    else
        set(gca, 'YScale', 'linear')
    end
    if handles.logfreq == 1
        set(gca,'xscale','log')
    end
%% End copied source
        else
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L882-L892
        figdata = figure;  
        set(gcf,'Color', 'white')
        plot(fd,po,'k-','LineWidth',1);
        hold on; 
        plot(fd,theored,'k-','LineWidth',2);
        plot(fd,tabtchi90,'r-','LineWidth',1);
        plot(fd,tabtchi95,'r--','LineWidth',2);
        plot(fd,tabtchi99,'b-.','LineWidth',1);
        plot(fd,tabtchi999,'g--','LineWidth',1);
        xlim([fmin fmax]);
        
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L894-L897
            xlabel(['Frequency (cycles/',num2str(unit),')'])
            ylabel('Power')
            title([num2str(nw),'\pi MTM classic AR1: \rho = ',num2str(rho),'; Sampling rate = ',num2str(dt),' ', unit,'; bw = ',num2str(bw)])
            legend('Power','AR1','90%','95%','99%','99.9%')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L914-L921
        if handles.linlogY == 1
            set(gca, 'YScale', 'log')
        else
            set(gca, 'YScale', 'linear')
        end
        if handles.logfreq == 1
            set(gca,'xscale','log')
        end
%% End copied source
        end
    else
        tabtchired90=c.tabtchired90; tabtchired95=c.tabtchired95; tabtchired99=c.tabtchired99;
        if plot_x_period
            pt1=1./fd1;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1541-L1545
            hold on
            plot(pt1,theored,'k-','LineWidth',2)
            plot(pt1,tabtchired90,'r-','LineWidth',1)
            plot(pt1,tabtchired95,'r--','LineWidth',2)
            plot(pt1,tabtchired99,'b-.','LineWidth',1)
%% End copied source
        else
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1571-L1575
            hold on
            plot(fd1,theored,'k-','LineWidth',2)
            plot(fd1,tabtchired90,'r-','LineWidth',1)
            plot(fd1,tabtchired95,'r--','LineWidth',2)
            plot(fd1,tabtchired99,'b-.','LineWidth',1)
%% End copied source
        end
    end
end
if isfield(m,'false_alarm')
    hold on; pfa=1-p.pd; pth=m.false_alarm;
    if plot_x_period
        fa=1./fd1;
    else
        fa=fd1;
    end
    plot(fa,pth*ones(size(fa')));
end
if isfield(m,'robust')
    z=m.robust;
    if strcmp(method,'Multi-taper method')
        redconfAR1=z.redconfAR1; redconfML96=z.redconfML96; rhoM=z.rhoM; s0M=z.s0M;
        if plot_x_period
            figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L6-L29
    clf;
    set(gcf,'Color', 'white')
    ft0 = redconfAR1(:,1);
    %disp(ft0(1))
    pt0 = 1./ft0;
    pxx0 = redconfAR1(:,2);
    pxxsmooth0 = redconfAR1(:,3);
    ft     = redconfML96(:,1);
    pt     = 1./ft;
    theored1 = redconfML96(:,3);
    chi90  = redconfML96(:,4);
    chi95  = redconfML96(:,5);
    chi99  = redconfML96(:,6);
    chi999 = redconfML96(:,7);

    semilogy(pt0,pxx0,'k')
    hold on; 
    semilogy(pt0,pxxsmooth0,'m-.');
    semilogy(pt,theored1,'k-','LineWidth',2);
    semilogy(pt,chi90,'r-');
    semilogy(pt,chi95,'r--','LineWidth',2);
    semilogy(pt,chi99,'b-.');
    semilogy(pt,chi999,'g--','LineWidth',1);
    hold off
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L31-L36
        xlabel(['Period (',num2str(unit),')']) 
        title([num2str(nw),'\pi-MTM-Robust-AR(1): \rho = ',num2str(rhoM),'. S0 = ',num2str(s0M)])
        ylabel('Power')
        smthwin = [num2str(smoothwin*100),'%', ' median-smoothed'];
        legend('Power',smthwin,'Robust AR(1) median',...
            'Robust AR(1) 90%','Robust AR(1) 95%','Robust AR(1) 99%','Robust AR(1) 99.9%')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L57-L76
    if fmin <= 0 
        fmin_s = pt(3);
    else
        fmin_s = 1/fmin;
    end
    
    xlim([1/fmax, fmin_s]);
    set(gca, 'XDir','reverse')
    
    set(gcf,'Name',[dat_name,ext,' ',num2str(nw),'pi MTM'])
    set(gca,'XMinorTick','on','YMinorTick','on')
    set(gcf,'Color', 'white')
    if handles.linlogY == 1
        set(gca, 'YScale', 'log')
    else
        set(gca, 'YScale', 'linear')
    end
    if handles.logfreq == 1
        set(gca,'xscale','log')
    end
%% End copied source
        else
            pxx=q.po; f0=q.fd1;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L491-L497
            f1 = redconfAR1(:,1);
            pxxsmooth0 = redconfAR1(:,3);
            f = redconfML96(:,1);
            theored1 = redconfML96(:,3);
            chi90 = redconfML96(:,4);
            chi95 = redconfML96(:,5);
            chi99 = redconfML96(:,6);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L499-L507
            figdata = figure; 
            set(gcf,'Color', 'white')
            semilogy(f0,pxx,'k')
            hold on; 
            semilogy(f1,pxxsmooth0,'m-.');
            semilogy(f,theored1,'k-','LineWidth',2);
            semilogy(f,chi90,'r-');
            semilogy(f,chi95,'r--','LineWidth',2);
            semilogy(f,chi99,'b-.');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L509-L512
                ylabel('Power')
                smthwin = [num2str(smoothwin*100),'%', ' median-smoothed'];
                legend('Power',smthwin,'Robust AR(1) median',...
                    'Robust AR(1) 90%','Robust AR(1) 95%','Robust AR(1) 99%')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L533-L534
            xlabel(['Frequency (cycles/',num2str(unit),')'])
            title([num2str(nw),'\pi-MTM-Robust-AR(1): \rho = ',num2str(rhoM),'. S0 = ',num2str(s0M),'; bw = ',num2str(bw)])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L541-L552
            xlim([fmin fmax]);
            set(gcf,'Name',[dat_name,ext,' ',num2str(nw),'pi MTM'])
            set(gca,'XMinorTick','on','YMinorTick','on')
            set(gcf,'Color', 'white')
            if handles.linlogY == 1
                set(gca, 'YScale', 'log')
            else
                set(gca, 'YScale', 'linear')
            end
            if handles.logfreq == 1
                set(gca,'xscale','log')
            end
%% End copied source
        end
    else
        f=z.f; po=z.po; pxxsmooth=z.pth(1,:); theored1=z.pth(2,:); chi90=z.pth(3,:); chi95=z.pth(4,:); chi99=z.pth(5,:);
        if plot_x_period
            f=1./f;
        end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/plomb_robustar1.m:L66-L75
    figure; 
    set(gcf,'Color', 'white')
    hold on; 
    %semilogy(f,chi999,'g--','LineWidth',1);
    semilogy(f,chi99,'b-.');
    semilogy(f,chi95,'r--','LineWidth',2);
    semilogy(f,chi90,'r-');
    semilogy(f,theored1,'k-','LineWidth',2);
    semilogy(f,pxxsmooth,'m-.');
    semilogy(f,po,'k')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/plomb_robustar1.m:L77-L82
    xlabel('Frequency')
    ylabel('Power')
    smthwin = [num2str(smoothwin*100),'%', ' median-smoothed'];
    legend( 'Robust AR(1) 99%', 'Robust AR(1) 95%','Robust AR(1) 90%',...
        'Robust AR(1) median',smthwin,'Power')
    set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
        if plot_x_period, set(gca,'XDir','reverse'); xlabel(['Period (',unit,')']); else, xlim([fmin fmax]); end
    end
end
if isfield(m,'ftest')
    z=m.ftest; lang_id=handles.lang_id; lang_var=handles.lang_var; freq=z.freq1; freq1=freq; ftest=z.ftest; fsigout=z.fsigout; Amp=z.Amp; Faz=z.Faz; dof=z.dof; NW=nw;
    if plot_x_period
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_spectral_x_period_mtm.m:L174-L260
    pt = 1./freq;
    
    figure;
    
    subplot(3,1,1)
    
    plot(pt, Amp,'color',[0, 0.4470, 0.7410],'LineWidth',1.5)
    if or(handles.lang_choice == 0, handles.main_unit_selection == 0)
        title(['Amplitude, F-test significance level : ', num2str(nw), '\pi'])
        ylabel('Amplitude')
    else
        [~, spectral45] = ismember('spectral45',lang_id);
        [~, spectral46] = ismember('spectral46',lang_id);
        title([lang_var{spectral45},', ',lang_var{spectral46},' : ', num2str(nw), '\pi'])
        ylabel(lang_var{spectral45})
    end
    
    if fmin <= 0 
        fmin_s = pt(3);
    else
        fmin_s = 1/fmin;
    end
    
    xlim([1/fmax, fmin_s]);
    set(gca, 'XDir','reverse')
    if handles.logfreq == 1
        set(gca,'xscale','log')
    end
    
    subplot(3,1,2)
    plot(pt, ftest,'color','k','LineWidth',1);
    if or(handles.lang_choice == 0, handles.main_unit_selection == 0)
        ylabel('F-ratio')
    else
        [~, spectral47] = ismember('spectral47',lang_id);
        ylabel(lang_var{spectral47})
    end
    if fmin <= 0 
        fmin_s = pt(3);
    else
        fmin_s = 1/fmin;
    end
    
    xlim([1/fmax, fmin_s]);
    set(gca, 'XDir','reverse')
    if handles.logfreq == 1
        set(gca,'xscale','log')
    end
    
    subplot(3,1,3)
    hold on
    fsigsh = 0.15;
    fsig1 = fsigout;
    fsig1(fsig1>fsigsh) = fsigsh;
    %yyaxis right
    plot(pt, fsig1,'color','red','LineWidth',1);
    ylim([0.0, fsigsh])
    line([pt(2) pt(end)],[.05 .05],'Color','m','LineWidth',0.35,'LineStyle','-.')
    line([pt(2) pt(end)],[.10 .10],'Color','k','LineWidth',0.5,'LineStyle',':')
    line([pt(2) pt(end)],[.01 .01],'Color','r','LineWidth',0.5,'LineStyle','--')
    yticks([0.0 0.01 0.05 0.10 0.15])
    yticklabels({'0','0.01','0.05','0.10','0.15'})
    
    if or(handles.lang_choice == 0, handles.main_unit_selection == 0)
        ylabel('F-test significance level')
        xlabel(['Period (',unit,')'])
    else
        [~, spectral46] = ismember('spectral46',lang_id);
        ylabel(lang_var{spectral46})
        [~, main15] = ismember('main15',lang_id);
        xlabel([lang_var{main15},' (',handles.unit,')'])
    end
    set(gca, 'YDir','reverse')
    if fmin <= 0 
        fmin_s = pt(3);
    else
        fmin_s = 1/fmin;
    end
    
    xlim([1/fmax, fmin_s]);
    set(gca, 'XDir','reverse')
    if handles.logfreq == 1
        set(gca,'xscale','log')
    end
    colordef white;
    set(gcf,'units','norm') % set location
    set(gcf,'position',[0.0,0.05,0.45,0.45])
%% End copied source
    else
        fnyq=1/(2*dt);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/ftestmtmML.m:L70-L97
    figure; 
    subplot(3,1,1)
    plot(freq1, Amp,'color',[0, 0.4470, 0.7410],'LineWidth',1.5)
    xlim([0, fnyq])
    title(['Amplitude, F-test & significance level : ', num2str(NW), '\pi'])
    ylabel('Amplitude')
    
    subplot(3,1,2)
    plot(freq1, ftest,'color','k','LineWidth',1);
    xlim([0, fnyq])
    ylabel('F-ratio')
    
    subplot(3,1,3)
    fsigsh = 0.15;
    fsig1 = fsigout;
    fsig1(fsig1>fsigsh) = fsigsh;
    %yyaxis right
    plot(freq1, fsig1,'color','red','LineWidth',1);
    ylim([0.0, fsigsh])
    xlim([0, fnyq])
    line([0 fnyq],[.10 .10],'Color','k','LineWidth',0.5,'LineStyle',':')
    line([0 fnyq],[.05 .05],'Color','m','LineWidth',0.35,'LineStyle','-.')
    line([0 fnyq],[.01 .01],'Color','r','LineWidth',0.5,'LineStyle','--')
    yticks([0.0 0.01 0.05 0.10 0.15])
    yticklabels({'0','0.01', '0.05', '0.10','0.15'})
    ylabel('F-test significance level')
    xlabel('Frequency')
    set(gca, 'YDir','reverse')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L935-L948
            subplot(3,1,1); xlim([fmin fmax])
            subplot(3,1,2); xlim([fmin fmax])
            subplot(3,1,3); xlim([fmin fmax])
            set(gcf,'color','white');
            set(gcf,'units','norm') % set location
            set(gcf,'position',[0.0,0.05,0.45,0.45])
            
            fig2 = figure;
            set(gcf,'color','white');
            set(gcf,'units','norm') % set location
            set(gcf,'position',[0.2,0.05,0.45,0.45])
            subplot(2,1,1); 
            plot(freq,dof,'color','k','LineWidth',1)
            xlim([fmin fmax])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L950-L950
                title('Adaptive weighted degrees of freedom')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L955-L957
            subplot(2,1,2); 
            plot(freq,Faz,'color','k','LineWidth',1)
            xlim([fmin fmax])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L959-L959
                title('Harmonic phase')
%% End copied source
    end
end
if isfield(m,'swa')
    outputdata=m.swa.outputdata;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L985-L993
        clfdr = outputdata(:, 9:13);
        xvalue = outputdata(:,1);
        pxx = outputdata(:,2);
        swa = outputdata(:,3);
        chi90 = outputdata(:,4);
        chi95 = outputdata(:,5);
        chi99 = outputdata(:,6);
        chi999 = outputdata(:,7);
        chi9999 = outputdata(:,8);
%% End copied source
    figure; if plot_x_period, xvalue=1./xvalue; end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1050-L1075
        hold on
        
        % plot FDR
        if ~isnan(clfdr(1,5))  % 0.01% FDR
            plot(xvalue, clfdr(:,5),'m-.','LineWidth',0.5,'DisplayName','0.01% FDR');
        end
        if ~isnan(clfdr(1,4))  % 0.1% FDR
            plot(xvalue, clfdr(:,4),'g-.','LineWidth',0.5,'DisplayName','0.1% FDR'); % 0.1% FDR
        end
        if ~isnan(clfdr(1,3))  % 1% FDR
            plot(xvalue, clfdr(:,3),'b--','LineWidth',0.5,'DisplayName','1% FDR'); % 1% FDR
        end
        if ~isnan(clfdr(1,2))  % 5% FDR
            plot(xvalue, clfdr(:,2),'r-.','LineWidth',2,'DisplayName','5% FDR'); % 5% FDR
        end
        %plot(xvalue,chi9999,'g:','LineWidth',0.5,'DisplayName','Chi2 99.99% CL')
        plot(xvalue,chi999,'m-.','LineWidth',0.5,'DisplayName','Chi2 99.9% CL')
        plot(xvalue,chi99,'b-.','LineWidth',0.5,'DisplayName','Chi2 99% CL')
        plot(xvalue,chi95,'r--','LineWidth',2,'DisplayName','Chi2 95% CL')
        plot(xvalue,chi90,'r-','LineWidth',0.5,'DisplayName','Chi2 90% CL')
        plot(xvalue,swa,'k-','LineWidth',1.5,'DisplayName','Backgnd')
        plot(xvalue, pxx,'k-','LineWidth',0.5,'DisplayName','Power'); 
        legend
        set(gca,'YScale','log');
        set(gca,'XMinorTick','on','YMinorTick','on')
        set(gcf,'Color', 'white')
%% End copied source
    if plot_x_period
        if fmin>0, maximum=1/fmin; else, maximum=xvalue(3); end
        xlim([1/fmax,maximum]); set(gca,'XDir','reverse');
    else, xlim([fmin,fmax]); end
end
if isfield(m,'powerlaw'), acmethods.SpectralPowerLaw.plotter(plotParams(m.powerlaw,p)); end
if isfield(m,'bending'), acmethods.SpectralBendingPowerLaw.plotter(plotParams(m.bending,p)); end
end

function q=plotParams(q,p)
fields={'plot_x_period','fmin','fmax','unit','logfreq','linlogY'};
for i=1:numel(fields), q.(fields{i})=p.(fields{i}); end
end

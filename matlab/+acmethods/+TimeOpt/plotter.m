function [retval, id] = plotter(params, id)
% TimeOpt.plotter parameters: sedmin sedmax fit targetE targetP genplot cormethod nsim result mc_scope.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/timeOptGUI.m#L378
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('TimeOpt-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
sedmin = p.sedmin;
sedmax = p.sedmax;
fit = p.fit;
targetE = p.targetE;
targetP = p.targetP;
genplot = p.genplot;
cormethod = p.cormethod;
nsim = p.nsim;
xx = p.result.xx;
xcl = p.result.xcl;
xsim = p.result.xsim;
datopt = p.result.datopt;
data = datopt(:,1:2);
tanhilb = datopt(:,[1,3,4]);
sedrate = xx(:,1);
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L138-L143
% precession amplitude modulation
if fit == 1
    targetTot = [targetE,targetP]; 
elseif fit == 2
    targetTot = targetE;
end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L212-L229
r2env = xx(:,2);
maxr2env = max(r2env);
locj = find(r2env == maxr2env);
if length(locj) > 1
    disp('>>  WARNING: Multiple envelope maxima detected.')
end
r2pwr = xx(:,3);
maxr2pwr = max(r2pwr);
locm = find(r2pwr == maxr2pwr);
if length(locm) > 1
    disp('>>  WARNING: Multiple spectral power maxima detected.')
end
r2opt = xx(:,4);
maxr2opt = max(r2opt);
loci = find(r2opt == maxr2opt);
if length(loci) > 1
    disp('>>  WARNING: Multiple (spectral power*envelope) maxima detected.')
end
%% End copied source
sedrate1 = sedrate(loci(1));
if fit == 1, target = targetE; else, target = targetE(1); end
timeSeries = tanhilb(:,[1,3]);
[~,datay] = fitItls(timeSeries,sedrate1,target,cormethod,1,0);
y=datay(:,2); fy=datay(:,3); datl=datay(:,4);
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/fitItls.m:L60-L82
if genplot == 1
    timeSeries(:,1) = timeSeries(:,1) - min(timeSeries(:,1));
    figure;
    set(gcf,'Name','Acycle: TimeOpt #1')
    set(gcf,'Units','normalized','Position',[0.0, 0.5, 0.33, 0.4])
    subplot(2,1,1)
    plot(timeSeries(:,1), y,'r','LineWidth',3);
    hold on;
    plot(timeSeries(:,1), fy,'k','LineWidth',2);
    %legend('Envolope','Reconstructed')
    title(['Envelope (red) vs. reconstructed model (black) @ ', num2str(sedrate1),' cm/kyr'])
    xlabel('Time (kyr)')
    ylabel('Std. Value')
    xlim([min(timeSeries(:,1)), max(timeSeries(:,1))])
    
    %figure;
    subplot(2,1,2)
    plot(y,fy,'ko','MarkerSize',10)
    hold on;
    plot(y,datl,'r--','LineWidth',3)
    xlabel('Envelope')
    ylabel('Reconstructed Model')
end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L256-L281
if genplot == 1
    figure;
    set(gcf,'Name','Acycle: TimeOpt #2')
    set(gcf,'Units','normalized','Position',[0.33, 0.5, 0.33, 0.4])
    subplot(2,1,1)
    plot(tanhilb(:,1),tanhilb(:,2),'b-','LineWidth',2);hold on;
    plot(tanhilb(:,1),tanhilb(:,3),'r','LineWidth',3);
    %legend('Taner filtered','Envolope')
    title(['Taner filtered (blue) vs. envelope (red) @ ', num2str(sedrate(loci(1))), ' cm/kyr'])
    xlabel('Time (kyr)')
    ylabel('Std. value')
    xlim([min(tanhilb(:,1)), max(tanhilb(:,1))])
    
    subplot(2,1,2)
    dt = median(diff(data(:,1)));
    [po,fd1]=periodogram(data(:,2),[],[],1/dt);
    plot(fd1,po,'k','LineWidth',1);
    xlabel('Frequency (cycles/kyr)') 
    ylabel('Power')
    title('Periodogram (black) vs. astronomical frequencies (dashed red)')
    xlim([0,.1])
    hold on;
    for i = 1: length(targetTot)
        line([1/targetTot(i) 1/targetTot(i)],[min(po) max(po)],'Color','red','LineStyle','--')
    end
end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L284-L386
if genplot == 1
    figure;
    
    set(gcf,'Name','Acycle: TimeOpt #3')
    set(gcf,'Units','normalized','Position',[0.66, 0.5, 0.33, 0.4])
    set(gcf,'color','w');
    
    subplot(3,1,1)
    plot(sedrate,xx(:,2),'ro','LineWidth',2);
    line([sedrate(locj(1)) sedrate(locj(1))],[min(xx(:,2)) max(xx(:,2))],'Color','red','LineStyle','--')
    %legend('r^2_e_n_v_e_l_o_p_e')
    xlabel('Sedimentation rate (cm/kyr)')
    ylabel('r^2_e_n_v_e_l_o_p_e')
    xlim([sedmin,sedmax])
    
    subplot(3,1,2)
    plot(sedrate,xx(:,3),'-','color',[0,0,0]+.5,'LineWidth',2);
    line([sedrate(locm(1)) sedrate(locm(1))],[min(xx(:,3)) max(xx(:,3))],'Color','red','LineStyle','--')
    %legend('r^2_p_o_w_e_r')
    xlabel('Sedimentation rate (cm/kyr)')
    ylabel('r^2_p_o_w_e_r')
    xlim([sedmin,sedmax])
    
    subplot(3,1,3)
    plot(sedrate,xx(:,4),'k-','LineWidth',3);
    line([sedrate(loci(1)) sedrate(loci(1))],[min(xx(:,4)) max(xx(:,4))],'Color','red','LineStyle','--')
    %legend('r^2_o_p_t')
    xlabel('Sedimentation rate (cm/kyr)')
    ylabel('r^2_o_p_t')
    xlim([sedmin,sedmax])
end

if genplot == 2
    figure;
    set(gcf,'Name','Acycle: TimeOpt Plot')
    set(gcf,'Units','normalized','Position',[0.06, 0.1, 0.8, 0.8])
    set(gcf,'color','w');
    
    subplot(3,2,1)
    plot(sedrate,xx(:,4),'k-','LineWidth',3);
    line([sedrate(loci(1)) sedrate(loci(1))],[min(xx(:,4)) max(xx(:,4))],'Color','red','LineStyle','--')
    xlabel('Sedimentation rate (cm/kyr)')
    ylabel('r^2')
    xlim([sedmin,sedmax])
    title('Optimal fit: r^2_o_p_t')
    %
    subplot(3,2,2)
    plot(datay(:,1), datay(:,2),'r','LineWidth',3);
    hold on;
    plot(datay(:,1), datay(:,3),'k','LineWidth',2);
    title(['Envelope (red) vs. reconstructed model (black) @ ', num2str(sedrate(loci(1))),' cm/kyr'])
    xlabel('Time (kyr)')
    ylabel('Std. value')
    xlim([min(datay(:,1)), max(datay(:,1))])
    
    subplot(3,2,3)
    yyaxis right
    plot(sedrate,xx(:,2),'ro','LineWidth',2);
    line([sedrate(locj(1)) sedrate(locj(1))],[min(xx(:,2)) max(xx(:,2))],'Color','red','LineStyle','--')
    xlabel('Sedimentation rate (cm/kyr)')
    ylabel('r^2')
    %ylabel('r^2_p_o_w_e_r')
    xlim([sedmin,sedmax])
    yyaxis left
    plot(sedrate,xx(:,3),'-','color',[0,0,0]+.5,'LineWidth',2);
    line([sedrate(locm(1)) sedrate(locm(1))],[min(xx(:,3)) max(xx(:,3))],'Color','red','LineStyle','--')
    %ylabel('r^2_e_n_v_e_l_o_p_e')
    xlim([sedmin,sedmax])
    title('Fit: r^2_e_n_v_e_l_o_p_e (red) vs. r^2_p_o_w_e_r (gray)')
    ax = gca;
    ax.YAxis(1).Color = [0,0,0]+.5;
    ax.YAxis(2).Color = 'r';
  
    subplot(3,2,4)
    plot(tanhilb(:,1),tanhilb(:,2),'b-','LineWidth',2);hold on;
    plot(tanhilb(:,1),tanhilb(:,3),'r','LineWidth',3);
    title(['Taner filtered (blue) vs. envelope (red) @ ', num2str(sedrate(loci(1))), ' cm/kyr'])
    xlabel('Time (kyr)')
    ylabel('Std. value')
    xlim([min(tanhilb(:,1)), max(tanhilb(:,1))])  
    
    subplot(3,2,5)
    plot(datay(:,2), datay(:,3),'ko','MarkerSize',10)
    hold on;
    plot(datay(:,2), datay(:,4),'r--','LineWidth',3)
    xlabel('Envelope')
    ylabel('Reconstructed model')
    title(['Envelope vs. reconstructed model (dot) @ ', num2str(sedrate(loci(1))),' cm/kyr & linear fit (red)'])
    
    subplot(3,2,6)
    dt = median(diff(data(:,1)));
    [po,fd1]=periodogram(data(:,2),[],[],1/dt);
    plot(fd1,po,'k','LineWidth',1);
    xlabel('Frequency (cycles/kyr)') 
    ylabel('Power')
    title('Periodogram (black) vs. astronomical frequencies (dashed red)')
    xlim([0,.1])
    hold on;
    for i = 1: length(targetTot)
        line([1/targetTot(i) 1/targetTot(i)],[min(po) max(po)],'Color','red','LineStyle','--')
    end
    
end
%% End copied source
if ~isempty(xcl)
    if strcmp(p.mc_scope,'all')
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L460-L507
        figure;
        set(gcf,'Units','normalized','Position',[0.1, 0.1, 0.4, 0.6])
        set(gcf,'Name','Acycle: TimeOpt Null Hypothesis Testing')
        set(gcf,'color','w');
        sr1 = min(sedrate);
        sr2 = max(sedrate);
        
        ax1 = subplot(3,1,1);
        semilogy(ax1, xcl(:,1),xcl(:,2),'r','LineWidth',1); 
        xlabel(ax1, 'Sedimentation rate (cm/kyr)')
        ylabel(ax1, 'H_0 significance level')
        title(ax1, 'r^2_e_n_v_e_l_o_p_e null hypothesis')
        ylim(ax1, [0.5*min(xcl(:,2)) 1])
        line([sr1, sr2],[.10, .10],'LineStyle',':','Color','k')
        line([sr1, sr2],[.05, .05],'LineStyle',':','Color','k')
        line([sr1, sr2],[.01, .01],'LineStyle','--','Color','k')
        line([sr1, sr2],[.001, .001],'LineStyle',':','Color','k')
        xlim(ax1,[sr1, sr2])
        %legend('H_0 Sig.level','10 %','5 %','1 %','0.1 %')
        set(ax1,'Ydir','reverse')
        
        ax2 = subplot(3,1,2);
        semilogy(ax2, xcl(:,1),xcl(:,3),'r','LineWidth',1); 
        xlabel(ax2, 'Sedimentation rate (cm/kyr)')
        ylabel(ax2, 'H_0 significance level')
        title(ax2, 'r^2_p_o_w_e_r null hypothesis')
        ylim(ax2, [0.5*min(xcl(:,3)) 1])
        line([sr1, sr2],[.10, .10],'LineStyle',':','Color','k')
        line([sr1, sr2],[.05, .05],'LineStyle',':','Color','k')
        line([sr1, sr2],[.01, .01],'LineStyle','--','Color','k')
        line([sr1, sr2],[.001, .001],'LineStyle',':','Color','k')
        %legend('H_0 Sig.level','10 %','5 %','1 %','0.1 %')
        xlim(ax2,[sr1, sr2])
        set(ax2,'Ydir','reverse')
        
        ax3 = subplot(3,1,3);
        semilogy(ax3, xcl(:,1),xcl(:,4),'r','LineWidth',1); 
        xlabel(ax3, 'Sedimentation rate (cm/kyr)')
        ylabel(ax3, 'H_0 significance level')
        title(ax3, 'r^2_o_p_t null hypothesis')
        ylim(ax3, [0.5*min(xcl(:,4)) 1])
        line([sr1, sr2],[.10, .10],'LineStyle',':','Color','k')
        line([sr1, sr2],[.05, .05],'LineStyle',':','Color','k')
        line([sr1, sr2],[.01, .01],'LineStyle','--','Color','k')
        line([sr1, sr2],[.001, .001],'LineStyle',':','Color','k')
        legend('H_0 Sig.level','10 %','5 %','1 %','0.1 %')
        xlim(ax3,[sr1, sr2])
        set(ax3,'Ydir','reverse')
%% End copied source
    else
        xs1=xsim(:,1);
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L532-L579
        figure;
        set(gcf,'Units','normalized','Position',[0.0, 0.05, 0.33, 0.4])
        set(gcf,'Name','Acycle: TimeOpt Null Hypothesis Testing')
        set(gcf,'color','w');
        xi=[];f=[];
        subplot(3,1,1)
        %[f,xi] = ksdensity(xsim(:,1));
        [f,xi] = ksdensity(xs1);
        X1 = [maxr2env,maxr2env];
        X2 = [maxr2pwr,maxr2pwr];
        Y = [0, 1.1*max(f)];

        plot(xi,f,'r','LineWidth',2);
        %legend('r^2_e_n_v_e_l_o_p_e')
        ylabel('# Simulations')
        ylim(Y)

        line(X1,Y,'Color','r','LineStyle','--','LineWidth',2)
        text(.6*maxr2env,.8*max(f),['r^2_e_n_v_e_l_o_p_e = ',num2str(maxr2env)],'Color','r')
        text(.6*maxr2env,.6*max(f),[' p-value = ',num2str(xcl(2),'%.5f')],'Color','r')
        title(['Null hypothesis at sedimentation rate of ', ...
            num2str(sedrate(loci(1)),'%.3f'),' cm/kyr. # simulations = ',num2str(nsim)])

        subplot(3,1,2)
        xi=[];f=[];
        [f,xi] = ksdensity(xsim(:,2));
        Y = [0, 1.1*max(f)];
        plot(xi,f,'color',[0,0,0]+.5,'LineWidth',2);
        %legend('r^2_p_o_w_e_r')
        ylabel('# Simulations')
        line(X2,Y,'Color',[0,0,0]+.5,'LineStyle','--','LineWidth',2)
        text(.6*maxr2pwr,.8*max(f),['r^2_p_o_w_e_r = ',num2str(maxr2pwr)],'Color',[0,0,0]+.5)
        text(.6*maxr2pwr,.6*max(f),[' p-value = ',num2str(xcl(3),'%.5f')],'Color',[0,0,0]+.5)
        ylim(Y)

        subplot(3,1,3)
        xi=[];f=[];
        [f,xi] = ksdensity(xsim(:,3));
        plot(xi,f,'k-','LineWidth',3);
        hold on
        %legend('r^2_o_p_t')
        ylabel('# Simulations')
        X = [maxr2opt, maxr2opt];
        Y = [0, 1.1*max(f)];
        line(X,Y,'Color','k','LineStyle','--')
        text(.6*maxr2opt,.8*max(f), ['r^2_o_p_t = ',num2str(maxr2opt)],'Color','k')
        text(.6*maxr2opt,.6*max(f),[' p-value = ',num2str(xcl(4),'%.5f')],'Color','k')
        ylim(Y)
%% End copied source
    end
end
r = [];
end

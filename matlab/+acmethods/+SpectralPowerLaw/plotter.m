function [retval, id] = plotter(params, id)
% SpectralPowerLaw.plotter parameters: fd1 po pl red90 red95 red99 red90global red95global red99global plot_x_period fmin fmax unit logfreq linlogY.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L604
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SpectralPowerLaw-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
fd1 = p.fd1;
po = p.po;
pl = p.pl;
red90 = p.red90;
red95 = p.red95;
red99 = p.red99;
red90global = p.red90global;
red95global = p.red95global;
red99global = p.red99global;
plot_x_period = p.plot_x_period;
fmin = p.fmin;
fmax = p.fmax;
unit = p.unit;
logfreq = p.logfreq;
linlogY = p.linlogY;
figure;
handles=struct('logfreq',logfreq,'linlogY',linlogY); pt=1./fd1;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L604-L607
        set(gcf,'Color', 'white')
        if plot_x_period
            pt1 = 1./fd1;
            plot(pt1(2:end),po(2:end),'k-','LineWidth',1);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L609-L609
                xlabel(['Period (',num2str(unit),')']) 
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L614-L632
            if fmin <= 0 
                fmin_s = pt(3);
            else
                fmin_s = 1/fmin;
            end

            xlim([1/fmax, fmin_s]);
            set(gca, 'XDir','reverse')
            hold on
            plot(pt1,red99global,'r-.','LineWidth',1)
            plot(pt1,red95global,'r--','LineWidth',2)
            plot(pt1,red90global,'r-','LineWidth',1)
            plot(pt1,red99,'b-.','LineWidth',1)
            plot(pt1,red95,'b--','LineWidth',2)
            plot(pt1,red90,'b-','LineWidth',1)
            plot(pt1,pl,'k-','LineWidth',2)
        else
            plot(fd1(2:end),po(2:end),'k-','LineWidth',1);
            xlim([fmin fmax]);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L634-L634
                xlabel(['Frequency (cycles/',num2str(unit),')']) 
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L639-L647
            hold on
            plot(fd1,red99global,'r-.','LineWidth',1)
            plot(fd1,red95global,'r--','LineWidth',2)
            plot(fd1,red90global,'r-','LineWidth',1)
            plot(fd1,red99,'b-.','LineWidth',1)
            plot(fd1,red95,'b--','LineWidth',2)
            plot(fd1,red90,'b-','LineWidth',1)
            plot(fd1,pl,'k-','LineWidth',2)
        end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L650-L651
            legend('Power','99% global','95% global','90% global','99% local','95% local','90% local','Power law')
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
r=[];
end

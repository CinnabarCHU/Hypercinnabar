function [retval, id] = plotter(params, id)
% PowerSpectrum.plotter parameters: fd1 po fmin fmax unit plot_x_period linlogY logfreq.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L604
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerSpectrum-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
fd1 = p.fd1;
po = p.po;
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
r=[];
end

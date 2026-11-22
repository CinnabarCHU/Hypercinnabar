function [retval, id] = plotter(params, id)
% EnsembleEMD.plotter parameters: t time_series imfs imfsn fd1 pow.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9122
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EnsembleEMD-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
t = p.t;
time_series = p.time_series;
imfs = p.imfs;
imfsn = p.imfsn;
fd1 = p.fd1;
pow = p.pow;
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9122-L9135
    subplot(imfsn + 1, 1, 1)
    plot(t,time_series);
    xlim([min(t), max(t)])
    
    ylabel('Raw data')
    pow = [];
    for k = 1:imfsn
        subplot(imfsn+1, 1, k+1);
        plot(t,imfs(:, k));
        xlim([min(t), max(t)])
        ylabel(['IMF', num2str(k)]);
        if k == 1
            title('EEMD')
        end
%% End copied source
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9143-L9157
    figure
    
    for k = 1:imfsn-1
        subplot(imfsn-1, 1, k);
        plot(fd1, pow(:,k), 'DisplayName', ['IMF ', num2str(k)])
        if k == 1
            title('2-pi MTM power spectra of IMFs')
        end
        ylabel(['IMF', num2str(k)]);
        ax = gca;
        % Turn on minor ticks for the x-axis
        ax.XAxis.MinorTick = 'on';
    end
    % Add labels, title, and legend
    xlabel('Frequency');
%% End copied source
r=[];
end

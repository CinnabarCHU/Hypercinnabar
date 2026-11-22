function [retval, id] = plotter(params, id)
% EMD.plotter parameters: imfsn pow fd1.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8997
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EMD-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
imfsn = p.imfsn;
pow = p.pow;
fd1 = p.fd1;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8997-L9029
    figure
    for k = 1:imfsn+1
        subplot(imfsn+1, 1, k);
        plot(fd1, pow(:,k))
        if k == 1
            ylabel('Raw')
        else
            ylabel(['IMF', num2str(k-1)]);
        end
        ax = gca;
        if k == 1
            title('2 pi MTM power spectra')
        end
        % Turn on minor ticks for the x-axis
        ax.XAxis.MinorTick = 'on';
    end
    
    % Add labels, title, and legend
    xlabel('Frequency');
    
    % figure
    figure
    hold on
    for k = 2:imfsn + 1
            plot(fd1, pow(:,k), 'DisplayName', ['IMF ', num2str(k-1)])
    end
    set(gca, 'YScale', 'log')
    title('2 pi MTM power spectra')
    ax.XAxis.MinorTick = 'on';
    xlabel('Frequency')
    ylabel('Power')
    legend
    hold off
%% End copied source
r=[];
end

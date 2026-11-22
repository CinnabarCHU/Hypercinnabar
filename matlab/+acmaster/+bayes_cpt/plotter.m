function [retval,id] = plotter(params,id)
% bayes_cpt.plotter parameters: x Y model chgpt_loc.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/bayes_cpt.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bayes_cpt-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
x = p.x;
Y = p.Y;
model = p.model;
chgpt_loc = p.chgpt_loc;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/bayes_changepoint/bayes_cpt.m:L258-L281
figure;
plot(x,Y, 'LineWidth', 2); 
hold on
title('Change Points', 'fontsize', 12)

[ax, h1, h2] = plotyy(x,model,x,chgpt_loc, 'plot');
gca=ax(1);
set(gca,'Ycolor', 'k')      % Left Y-axis colored black
set(gca, 'fontsize', 12)    % Default is 10
set(get(ax(1), 'Ylabel'), 'String', 'Proxy', 'fontsize', 12)
set(h1, 'Color', 'g')       % Model plotted in green, default blue
set(h1, 'LineStyle', '--'); % Default is a solid line
set(h1, 'LineWidth', 2)     % Default is 0.5

gca=ax(2);
set(gca, 'Ylim', [0 2])
set(gca, 'Ycolor', 'r')     % Right Y-Axis colored red
set(gca, 'Yticklabel', 0:0.1:1)
set(gca, 'Ytick', 0:0.1:1)
set(gca, 'fontsize', 12)
set(get(ax(2), 'Ylabel'), 'String', 'Posterior Probability', 'fontsize', 12)
set(h2, 'Color', 'r')       % Posterior probabilities plotted in red
set(h2, 'LineWidth', 2)
hold off
%% End copied source
r=[];
end

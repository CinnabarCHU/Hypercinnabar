function [retval, id] = plotter(params, id)
% Lyapunov.plotter parameters: result unit_type unit tau window step_size.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9807
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lyapunov-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
handles=p; output=p.result.output; data=p.result.data; t=data(:,1);
tau = p.tau;
window = p.window;
step_size = p.step_size;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9807-L9815
                            figure;
                            set(gcf,'Color', 'white')
                            subplot(2,1,1)
                            plot(data(:,1),data(:,2),'LineWidth',1)
                            xlim([min(t), max(t)])
                            subplot(2,1,2)
                            plot(output(:,1),output(:,2),'LineWidth',1)
                            set(gca, 'YDir', 'reverse');
                            xlim([min(t), max(t)])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9817-L9825
                                if handles.unit_type == 0
                                    xlabel(['Unit (',handles.unit,')'])
                                elseif handles.unit_type == 1
                                    xlabel(['Depth (',handles.unit,')'])
                                else
                                    xlabel(['Time (',handles.unit,')'])
                                end
                                ylabel('Lyapunov exponent')
                                title(['Tau = ', num2str(tau),'. Window = ',num2str(window),'. Step size = ',num2str(step_size)])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9838-L9838
                            set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
r=[];
end

function [retval, id] = plotter(params, id)
% Lag1MonteCarlo.plotter parameters: y_grid powyp y_grid_nan powyad_p_nan npercent npercent2 unit_type unit window1 window2 samprate1 samprate2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5588
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lag1MonteCarlo-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
y_grid = p.y_grid;
powyp = p.powyp;
y_grid_nan = p.y_grid_nan;
powyad_p_nan = p.powyad_p_nan;
npercent = p.npercent;
npercent2 = p.npercent2;
unit_type = p.unit_type;
unit = p.unit;
window1 = p.window1;
window2 = p.window2;
samprate1 = p.samprate1;
samprate2 = p.samprate2;
handles=struct('unit',unit,'unit_type',unit_type);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5588-L5601
                            figure;hold all
                            colorcode = [221/255,234/255,224/255; ...
                            201/255,227/255,209/255; ...
                            176/255,219/255,188/255;...
                            126/255,201/255,146/255;...
                            67/255,180/255,100/255];
                            for i = 1:npercent2
                                fill([y_grid_nan; (fliplr(y_grid_nan'))'],[powyad_p_nan(:,npercent+1-i);...
                                (fliplr(powyad_p_nan(:,i)'))'],colorcode(i,:),'LineStyle','none');
                            end
                            plot(y_grid,powyp(:,npercent2+1),'Color',[0,120/255,0],'LineWidth',1.5,'LineStyle','--')
                            hold off

                            set(gca,'XMinorTick','on','YMinorTick','on')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5604-L5614
                                if handles.unit_type == 0
                                    xlabel(['Unit (',handles.unit,')'])
                                elseif handles.unit_type == 1
                                    xlabel(['Depth (',handles.unit,')'])
                                else
                                    xlabel(['Time (',handles.unit,')'])
                                end
                                ylabel('RHO in AR(1)')
                                legend('2.5% - 97.5%', '5% - 95%', '10% - 90%','15.87% - 84.14%', '25% - 75%', 'Median')
                                title(['Window',': ',num2str(window1),'_',num2str(window2),...
                                    '. ','Sampling Rate',': ',num2str(samprate1),'_',num2str(samprate2)], 'Interpreter', 'none')
%% End copied source
r=[];
end

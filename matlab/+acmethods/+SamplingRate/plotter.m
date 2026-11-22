function [retval, id] = plotter(params, id)
% SamplingRate.plotter parameters: datasamp dt dat_name ext unit unit_type.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5825
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SamplingRate-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
datasamp = p.datasamp;
dt = p.dt;
dat_name = p.dat_name;
ext = p.ext;
unit = p.unit;
unit_type = p.unit_type;
handles=struct('unit',unit,'unit_type',unit_type);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5825-L5825
            figure;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5828-L5830
            stairs(datasamp(:,1),datasamp(:,2),'LineWidth',1,'Color','k');
            set(gca,'XMinorTick','on','YMinorTick','on')
            set(gcf,'Color', 'white')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5832-L5833
            set(gcf,'units','norm') % set location
            set(gcf,'position',[0.1,0.4,0.45,0.45]) % set position
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5836-L5847
                set(gcf,'Name', 'Sampling rate (original domain)','NumberTitle','off')
                if handles.unit_type == 0
                    xlabel(['Unit (',handles.unit,')'])
                    ylabel('Unit')
                elseif handles.unit_type == 1
                    xlabel(['Depth (',handles.unit,')'])
                    ylabel(handles.unit)
                else
                    xlabel(['Time (',handles.unit,')'])
                    ylabel(handles.unit)
                end
                title([[dat_name,ext],': ','sampling rate'], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5865-L5873
            xlim([min(datasamp(:,1)),max(datasamp(:,1))])
            ylim([0.9*min(dt) max(dt)*1.1])
            
            figure;
            histfit(dt,[],'kernel')
            set(gcf,'Color', 'white')
            set(0,'Units','normalized') % set units as normalized
            set(gcf,'units','norm') % set location
            set(gcf,'position',[0.55,0.4,0.45,0.45]) % set position
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5877-L5889
                title([[dat_name,ext],': kernel fit of sampling rates'], 'Interpreter', 'none')
                set(gcf,'Name', 'Sampling rate: distribution','NumberTitle','off')
                if handles.unit_type == 0
                    xlabel(['Sampling rate (',handles.unit,')'])
                elseif handles.unit_type == 1
                    xlabel(['Sampling rate (',handles.unit,')'])
                else
                    xlabel(['Sampling rate (',handles.unit,')'])
                end
                ylabel('Number')
                note = ['max: ',num2str(max(dt)),'; mean: ',num2str(mean(dt)),...
                    '; median: ',num2str(median(dt)),'; min: ',num2str(min(dt)),...
                    '; variance: ',num2str(var(dt))];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5905-L5905
            legend(note)
%% End copied source
r=[];
end

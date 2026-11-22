function [retval, id] = plotter(params, id)
% DataDistribution.plotter parameters: data_filterout dat_name ext.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5977
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DataDistribution-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
dat_name = p.dat_name;
ext = p.ext;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5977-L5980
            datax = data_filterout(:,2);
            figure;
            set(gcf,'Color', 'white')
            histfit(datax,[],'kernel')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5982-L5987
                set(gcf,'Name', 'Data Distribution','NumberTitle','off')
                title([[dat_name,ext],': kernel fit of the data'], 'Interpreter', 'none')
                xlabel('Data')
                note = ['max: ',num2str(max(datax)),'; mean: ',num2str(mean(datax)),...
                    '; median: ',num2str(median(datax)),'; min: ',num2str(min(datax)),...
                    '; variance: ',num2str(var(datax))];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5996-L5997
            legend(note)
            ylabel('#')
%% End copied source
r=[];
end

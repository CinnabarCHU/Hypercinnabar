function [retval,id] = plotter(params,id)
% DataDistribution.plotter parameters: data_filterout dat_name ext.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DataDistribution-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
dat_name = p.dat_name;
ext = p.ext;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7077-L7080
            datax = data_filterout(:,2);
            figure;
            set(gcf,'Color', 'white')
            histfit(datax,[],'kernel')
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7082-L7087
                set(gcf,'Name', 'Data Distribution','NumberTitle','off')
                title([[dat_name,ext],': kernel fit of the data'], 'Interpreter', 'none')
                xlabel('Data')
                note = ['max: ',num2str(max(datax)),'; mean: ',num2str(mean(datax)),...
                    '; median: ',num2str(median(datax)),'; min: ',num2str(min(datax)),...
                    '; variance: ',num2str(var(datax))];
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7096-L7097
            legend(note)
            ylabel('#')
%% End copied source
r=[];
end

function [retval,id] = plotter(params,id)
% ExampleExtinction.plotter parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ExampleExtinction-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8867-L8872
figure;
scatter(data,data,200,[0 0.4470 0.7410],'filled','MarkerFaceAlpha',0.5);
xlim([0 300])
ylim([0 300])
xlabel('Ma')
ylabel('Ma')
%% End copied source
r=[];
end

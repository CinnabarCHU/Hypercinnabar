function [retval,id] = plotter(params,id)
% ExampleWayao.plotter parameters: data data_name.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ExampleWayao-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
data = p.data;
data_name = p.data_name;
[~,dat_name,ext]=fileparts(data_name);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8806-L8810
time = data(:,1);
value = data(:,2);
figure;
plot(time,value)
title([dat_name,ext], 'Interpreter', 'none')
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8846-L8847
    xlabel('Depth (m)')
    ylabel('Gamma ray (cpm)')
%% End copied source
r=[];
end

function [retval,id] = plotter(params,id)
% ExampleNewark.plotter parameters: data data_name.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ExampleNewark-v3.1.1+dcba427/plotter',params,id,@execute);
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
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L9119-L9120
    xlabel('Depth (m)')
    ylabel('Depth Rank')
%% End copied source
r=[];
end

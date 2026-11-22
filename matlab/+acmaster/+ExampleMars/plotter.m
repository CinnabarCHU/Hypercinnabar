function [retval,id] = plotter(params,id)
% ExampleMars.plotter parameters: im_name data_name.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ExampleMars-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
im_name = p.im_name;
data_name = p.data_name;
[~,dat_name,ext]=fileparts(data_name);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7788-L7790
                figure;
                imshow(im_name)
                set(gcf,'Name',[dat_name,ext],'NumberTitle','off')
%% End copied source
r=[];
end

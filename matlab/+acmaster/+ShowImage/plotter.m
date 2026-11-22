function [retval,id] = plotter(params,id)
% ShowImage.plotter parameters: im_name.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ShowImage-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
im_name = p.im_name;
figure;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7789-L7789
                imshow(im_name)
%% End copied source
r=[];
end

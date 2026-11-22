function [retval,id] = plotter(params,id)
% RGBToGray.plotter parameters: I.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('RGBToGray-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
I = p.I;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5120-L5121
                        figure
                        imshow(I)
%% End copied source
r=[];
end

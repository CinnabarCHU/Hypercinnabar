function [retval,id] = plotter(params,id)
% RGBToLab.plotter parameters: I.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('RGBToLab-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
I = p.I;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5172-L5181
                        figure
                        subplot(3,1,1)
                        imshow(I(:,:,1),[0 100])
                        title('L*')
                        subplot(3,1,2)
                        imshow(I(:,:,2),[-128 127])
                        title('a*')
                        subplot(3,1,3)
                        imshow(I(:,:,3),[-128 127])
                        title('b*')
%% End copied source
r=[];
end

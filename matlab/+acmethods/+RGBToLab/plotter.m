function [retval, id] = plotter(params, id)
% RGBToLab.plotter parameters: I.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4121
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('RGBToLab-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
I = p.I;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4121-L4130
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

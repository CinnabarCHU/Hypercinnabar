function [retval, id] = plotter(params, id)
% ShowImage.plotter parameters: im_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8140
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ShowImage-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
im_name = p.im_name;
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8140-L8140
    imshow(im_name)
%% End copied source
r=[];
end

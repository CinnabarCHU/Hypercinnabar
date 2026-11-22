function [retval, id] = plotter(params, id)
% RGBToGray.plotter parameters: I.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4069
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('RGBToGray-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
I = p.I;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4069-L4070
                        figure
                        imshow(I)
%% End copied source
r=[];
end

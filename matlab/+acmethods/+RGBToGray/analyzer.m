function [retval, id] = analyzer(params, id)
% RGBToGray.analyzer parameters: im_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4068
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('RGBToGray-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
im_name = p.im_name;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4068-L4068
                        I = rgb2gray(im_name);
%% End copied source
r = struct();
r.I = I;
end

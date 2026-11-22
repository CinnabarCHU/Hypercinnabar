function [retval, id] = plotter(params, id)
% imscrollpanel_ac.plotter parameters: im_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/imscrollpanel_ac.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('imscrollpanel_ac-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
imscrollpanel_ac(p.im_name);
r = [];
end

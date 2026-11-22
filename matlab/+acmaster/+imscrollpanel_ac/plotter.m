function [retval,id] = plotter(params,id)
% imscrollpanel_ac.plotter parameters: im_name.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/imscrollpanel_ac.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('imscrollpanel_ac-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
imscrollpanel_ac(p.im_name);
r = [];
end

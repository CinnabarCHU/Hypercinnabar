function [retval, id] = helper(params, id)
% PassFilter.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/ft.m#L242
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/ft.fig
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PassFilter-v1.0/helper', params, id, @execute);
end

function r = execute(p)
base=acmethods.Bandpass.helper(p);
r=struct('data',base.data,'passtype','highpassiir','filter_s','Butter','f11',[], ...
    'f12',[],'x_1',base.x_1,'x_2',base.x_2,'y_1',base.y_1,'y_2',base.y_2);
end

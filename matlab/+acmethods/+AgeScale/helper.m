function [retval, id] = helper(params, id)
% AgeScale.helper parameters: data tiepoints.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L320
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L440
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AgeScale-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r=p; r.view='series'; r.unit=''; r.filename='';
validateattributes(p.data,{'numeric'},{'2d','nonempty'});
validateattributes(p.tiepoints,{'numeric'},{'2d','nonempty'});
end

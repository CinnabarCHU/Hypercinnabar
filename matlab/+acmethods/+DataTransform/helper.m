function [retval, id] = helper(params, id)
% DataTransform.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L70
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L94
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L100
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L106
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L115
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L132
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DataTransform-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r=p;
% Column two starts selected; the source leaves the transform choice to the user.
if size(p.data,2)>=2, r.checkid=2; else, r.checkid=[]; end
r.edit1=0; r.edit2=1; r.edit3=10; r.edit4=2;
end

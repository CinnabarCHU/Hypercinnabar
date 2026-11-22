function [retval, id] = analyzer(params, id)
% ImageProfile.analyzer parameters: I CursorInfo_value.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4305
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ImageProfile-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
I = p.I;
CursorInfo_value = p.CursorInfo_value;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4305-L4305
                                [cx,cy,c,xi,yi] = improfile(I,CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
r = struct();
r.cx = cx;
r.cy = cy;
r.c = c;
r.xi = xi;
r.yi = yi;
end

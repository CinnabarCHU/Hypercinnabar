function [retval,id] = analyzer(params,id)
% ImageProfile.analyzer parameters: I CursorInfo_value.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ImageProfile-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
I = p.I;
CursorInfo_value = p.CursorInfo_value;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5356-L5356
                                [cx,cy,c,xi,yi] = improfile(I,CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
r = struct();
r.cx = cx;
r.cy = cy;
r.c = c;
r.xi = xi;
r.yi = yi;
end

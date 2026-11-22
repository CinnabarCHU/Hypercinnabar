function [retval,id] = helper(params,id)
% LR04.helper parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('LR04-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4097-L4097
defaultans = {'0','5320'};
%% End copied source
t1=str2double(defaultans{1});
t2=str2double(defaultans{2});
r = struct();
r.t1 = t1;
r.t2 = t2;
end

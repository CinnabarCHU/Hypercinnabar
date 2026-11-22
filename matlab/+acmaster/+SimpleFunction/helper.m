function [retval,id] = helper(params,id)
% SimpleFunction.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SimpleFunction-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4755-L4755
            defaultans = {'1','0','1','0'};
%% End copied source
a=str2double(defaultans{1});
b=str2double(defaultans{2});
c=str2double(defaultans{3});
d=str2double(defaultans{4});
r = struct();
r.data = data;
r.a = a;
r.b = b;
r.c = c;
r.d = d;
end

function [retval,id] = analyzer(params,id)
% SimpleFunction.analyzer parameters: data a b c d.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SimpleFunction-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
a = p.a;
b = p.b;
c = p.c;
d = p.d;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4764-L4765
            data(:,1) = a * data(:,1) + b;
            data(:,2) = c * data(:,2) + d;
%% End copied source
r = struct();
r.data = data;
end

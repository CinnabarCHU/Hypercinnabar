function [retval,id] = helper(params,id)
% Extrema.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Extrema-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
x=data(:,1);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4834-L4834
            defaultans = {num2str(min(x)),num2str(max(x)),'1','2'};
%% End copied source
t1=str2double(defaultans{1}); t2=str2double(defaultans{2}); maxmin=str2double(defaultans{3}); ind=str2double(defaultans{4});
r = struct();
r.data = data;
r.t1 = t1;
r.t2 = t2;
r.maxmin = maxmin;
r.ind = ind;
end

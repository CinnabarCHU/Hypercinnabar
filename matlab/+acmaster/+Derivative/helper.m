function [retval,id] = helper(params,id)
% Derivative.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Derivative-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L1371-L1371
handles.math_derivative = 1;
%% End copied source
derivative_n=handles.math_derivative;
r = struct();
r.data = data;
r.derivative_n = derivative_n;
end

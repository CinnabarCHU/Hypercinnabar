function [retval, id] = helper(params, id)
% Derivative.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L613
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Derivative-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L613-L613
handles.math_derivative = 1;
%% End copied source
derivative_n=handles.math_derivative;
r = struct();
r.data = data;
r.derivative_n = derivative_n;
end

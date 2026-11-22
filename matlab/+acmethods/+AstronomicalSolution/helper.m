function [retval, id] = helper(params, id)
% AstronomicalSolution.helper parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/basicseries.m#L139
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AstronomicalSolution-v1.0/helper', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L139-L142
handles.solution = 'La2004';
handles.parameter = 'ETP';
handles.t1 = 0;
handles.t2 = 1000;
%% End copied source
solution=handles.solution; parameter=handles.parameter; t1=handles.t1; t2=handles.t2; wE=1; wT=1; wP=1;
r = struct();
r.solution = solution;
r.parameter = parameter;
r.t1 = t1;
r.t2 = t2;
r.wE = wE;
r.wT = wT;
r.wP = wP;
end

function [retval, id] = analyzer(params, id)
% LR04.analyzer parameters: t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3059
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LR04-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
t1 = p.t1;
t2 = p.t2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3059-L3060
    LR04stack = load('LR04stack5320ka.txt');
    LR04stack_s = select_interval(LR04stack,t1,t2);
%% End copied source
r = struct();
r.LR04stack_s = LR04stack_s;
r.t1 = t1;
r.t2 = t2;
end

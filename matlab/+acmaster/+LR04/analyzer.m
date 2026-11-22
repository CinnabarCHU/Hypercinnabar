function [retval,id] = analyzer(params,id)
% LR04.analyzer parameters: t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('LR04-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
t1 = p.t1;
t2 = p.t2;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4103-L4104
    LR04stack = load('LR04stack5320ka.txt');
    LR04stack_s = select_interval(LR04stack,t1,t2);
%% End copied source
r = struct();
r.LR04stack_s = LR04stack_s;
r.t1 = t1;
r.t2 = t2;
end

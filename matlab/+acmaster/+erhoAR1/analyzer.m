function [retval,id] = analyzer(params,id)
% erhoAR1.analyzer parameters: data window.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/erhoAR1.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('erhoAR1-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rhox] = erhoAR1(p.data, p.window);
r = struct();
r.rhox = rhox;
end

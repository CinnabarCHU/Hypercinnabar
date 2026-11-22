function [retval,id] = analyzer(params,id)
% theoredar1ML.analyzer parameters: datax f meanp dt.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/theoredar1ML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('theoredar1ML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[theored] = theoredar1ML(p.datax, p.f, p.meanp, p.dt);
r = struct();
r.theored = theored;
end

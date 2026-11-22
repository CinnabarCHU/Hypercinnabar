function [retval,id] = analyzer(params,id)
% dynotIterationWorker.analyzer parameters: data yGrid sample window nw targetBands options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/dynotIterationWorker.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('dynotIterationWorker-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[column, powerMean] = dynotIterationWorker(p.data, p.yGrid, p.sample, p.window, p.nw, p.targetBands, p.options);
r = struct();
r.column = column;
r.powerMean = powerMean;
end

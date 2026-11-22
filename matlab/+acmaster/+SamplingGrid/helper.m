function [retval,id] = helper(params,id)
% SamplingGrid.helper parameters: coordinate.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSamplingIsUneven.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SamplingGrid-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/acycleSamplingIsUneven.m:L12-L12
    relativeTolerance = 1e-5;
%% End copied source
r = p;
r.relativeTolerance = relativeTolerance;
end

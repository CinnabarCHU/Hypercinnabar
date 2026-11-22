function [retval,id] = analyzer(params,id)
% AgeScale.analyzer parameters: data agemodel.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/agescale.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('AgeScale-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data; agemodel = p.agemodel;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/agescale.m:L351-L352
                [time,~] = depthtotime(data(:,1),agemodel);
                tunedseries = [time,data(:,2)];
%% End copied source
r = struct();
r.time = time;
r.tunedseries = tunedseries;
end

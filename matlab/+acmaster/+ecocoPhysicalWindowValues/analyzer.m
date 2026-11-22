function [retval,id] = analyzer(params,id)
% ecocoPhysicalWindowValues.analyzer parameters: data window centers nominalDt options(MinimumSourcePoints).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoPhysicalWindowValues.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoPhysicalWindowValues-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'MinimumSourcePoints'});
[values, info] = ecocoPhysicalWindowValues( ...
    p.data, p.window, p.centers, p.nominalDt,  ...
    'MinimumSourcePoints',p.options.MinimumSourcePoints);
r = struct();
r.values = values;
r.info = info;
end

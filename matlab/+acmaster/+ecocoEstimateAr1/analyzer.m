function [retval,id] = analyzer(params,id)
% ecocoEstimateAr1.analyzer parameters: values.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoEstimateAr1.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoEstimateAr1-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rho, dataStd, valid] = ecocoEstimateAr1(p.values);
r = struct();
r.rho = rho;
r.dataStd = dataStd;
r.valid = valid;
end

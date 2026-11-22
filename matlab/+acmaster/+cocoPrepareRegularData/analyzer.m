function [retval,id] = analyzer(params,id)
% cocoPrepareRegularData.analyzer parameters: rawData label options(MaximumPoints,MinimumPoints,Verbose).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoPrepareRegularData.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoPrepareRegularData-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'MaximumPoints','MinimumPoints','Verbose'});
[data, info, clean] = cocoPrepareRegularData( ...
    p.rawData, p.label, 'MaximumPoints',p.options.MaximumPoints,  ...
    'MinimumPoints',p.options.MinimumPoints, 'Verbose',p.options.Verbose);
r = struct();
r.data = data;
r.info = info;
r.clean = clean;
end

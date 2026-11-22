function [retval,id] = plotter(params,id)
% plotAdaptiveCocoPublication.plotter parameters: corrCI corrH0 details report options(TitlePrefix,Visible).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/plotAdaptiveCocoPublication.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('plotAdaptiveCocoPublication-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'TitlePrefix','Visible'});
plotAdaptiveCocoPublication( ...
    p.corrCI, p.corrH0, p.details, p.report, 'TitlePrefix',p.options.TitlePrefix,  ...
    'Visible',p.options.Visible);
r = [];
end

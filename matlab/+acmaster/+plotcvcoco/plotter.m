function [retval,id] = plotter(params,id)
% plotcvcoco.plotter parameters: result options(ShowSpectra,Tabbed).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/plotcvcoco.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('plotcvcoco-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'ShowSpectra','Tabbed'});
plotcvcoco(p.result, 'ShowSpectra',p.options.ShowSpectra, 'Tabbed',p.options.Tabbed);
r = [];
end

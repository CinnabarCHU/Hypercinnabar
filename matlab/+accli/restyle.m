function next = restyle(source,destination,target)
% Copy explicitly chosen layout settings to the destination's own results.
if nargin < 3, target = []; end
style = source.explicit.plt;
if ~strcmp(source.operation,destination.operation) && (isfield(style,'panel') || isfield(style,'figureIndex'))
    error('Acycle:CLI:Panel','Select a corresponding panel explicitly when changing operations.');
end
next = accli.replot(destination,style,target);
end

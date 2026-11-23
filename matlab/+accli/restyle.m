function next = restyle(source,destination,target)
% Copy explicitly chosen layout settings to the destination's own results.
if nargin < 3, target = []; end
style = source.explicit.plt;
if ~strcmp(source.operation,destination.operation) && (isfield(style,'figureIndex') || ...
        (isfield(style,'panel') && isnumeric(style.panel)))
    error('Acycle:CLI:Panel','Select a named panel when transferring a layout across operations.');
end
next = accli.replot(destination,style,target);
end

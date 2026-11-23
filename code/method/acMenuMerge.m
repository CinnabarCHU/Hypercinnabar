function value = acMenuMerge(value,changes)
% Merge only scalar structs recursively. Supplied empty, false and zero are values.
if ~(isstruct(value) && isscalar(value) && isstruct(changes) && isscalar(changes))
    error('Acycle:Menu:Struct','Expected a scalar parameter structure.');
end
names = fieldnames(changes);
for k=1:numel(names)
    name = names{k};
    supplied = changes.(name);
    if isfield(value,name) && isstruct(value.(name)) && isscalar(value.(name)) && ...
            isstruct(supplied) && isscalar(supplied)
        value.(name) = acMenuMerge(value.(name),supplied);
    else
        value.(name) = supplied;
    end
end
end

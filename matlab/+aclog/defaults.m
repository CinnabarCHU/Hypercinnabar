function values = defaults(supplied, names, required, resolve)
% Evaluate the original positional defaults with the explicit prefix as context.
% Later user overrides are kept and participate in subsequent default decisions.
args = cell(1, numel(names));
values = supplied;
for k = 1:numel(names)
    name = names{k};
    if isfield(supplied, name)
        args{k} = supplied.(name);
    elseif k <= required
        error('Acycle:Method:Input', 'Missing input %s.', name);
    else
        derived = resolve(args{1:k-1});
        if ~isfield(derived, name)
            error('Acycle:Method:Input', 'The source requires an explicit %s.', name);
        end
        args{k} = derived.(name);
    end
    values.(name) = args{k};
end
end

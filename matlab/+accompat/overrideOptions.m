function options = overrideOptions(options,overrides)
% Apply caller changes to an upstream set of recommendations.
if ~isstruct(overrides) || ~isscalar(overrides)
    error('Acycle:Method:Options','Expected a scalar options structure.');
end
fields = fieldnames(overrides);
for index = 1:numel(fields)
    name = fields{index};
    if ~isfield(options,name)
        error('Acycle:Method:UnknownOption','Unknown option: %s.',name);
    end
    options.(name) = overrides.(name);
end
end

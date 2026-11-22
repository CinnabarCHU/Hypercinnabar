function requireFields(options,required)
% Reject incomplete active options before a numerical method can use hidden defaults.
if ~isstruct(options) || ~isscalar(options)
    error('Acycle:Method:Options','Expected a scalar options structure.');
end
missing = setdiff(required,fieldnames(options),'stable');
if ~isempty(missing)
    error('Acycle:Method:MissingOption','Required option(s): %s.',strjoin(missing,', '));
end
end

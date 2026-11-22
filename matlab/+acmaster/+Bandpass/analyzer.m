function [retval,id] = analyzer(params,id)
% Bandpass.analyzer parameters: data options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleBandpassFilter.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Bandpass-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
if strcmpi(p.options.method,'taner_hilbert')
    accompat.requireFields(p.options,{'rolloff_exponent'});
    if isempty(p.options.rolloff_exponent), error('Acycle:Method:MissingOption','Supply a finite rolloff exponent.'); end
end
[result, meta] = acycleBandpassFilter(p.data, p.options);
r = struct();
r.result = result;
r.meta = meta;
end

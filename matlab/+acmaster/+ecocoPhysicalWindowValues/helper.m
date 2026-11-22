function [retval,id] = helper(params,id)
% ecocoPhysicalWindowValues.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoPhysicalWindowValues.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoPhysicalWindowValues-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options.MinimumSourcePoints = 2;
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end

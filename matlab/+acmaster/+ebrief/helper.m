function [retval,id] = helper(params,id)
% ebrief.helper parameters: X dim a.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ebrief.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ebrief-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'X', 'dim', 'a'}, 1, @legacyDefaults);
end

function values = legacyDefaults(X, dim, a)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/ebrief.m:L12-L20
if nargin > 4
    error('Too many input arguments')
end
if nargin < 3
    a = 0;
if nargin < 2
    dim = 1;
end
end
%% End copied source
values = struct();
if exist('X', 'var'), values.X = X; end
if exist('dim', 'var'), values.dim = dim; end
if exist('a', 'var'), values.a = a; end
end

function [retval,id] = helper(params,id)
% findnpk.helper parameters: dat n o.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/findnpk.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('findnpk-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'dat', 'n', 'o'}, 1, @legacyDefaults);
end

function values = legacyDefaults(dat, n, o)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/findnpk.m:L11-L12
if nargin < 3; o=1;end
if nargin < 2; n=1;end
%% End copied source
values = struct();
if exist('dat', 'var'), values.dat = dat; end
if exist('n', 'var'), values.n = n; end
if exist('o', 'var'), values.o = o; end
end

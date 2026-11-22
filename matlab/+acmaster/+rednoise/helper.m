function [retval,id] = helper(params,id)
% rednoise.helper parameters: N g a.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/rednoise.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('rednoise-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'N', 'g', 'a'}, 2, @legacyDefaults);
end

function values = legacyDefaults(N, g, a)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/rednoise.m:L44-L46
if nargin<3
    a=1;
end
%% End copied source
values = struct();
if exist('N', 'var'), values.N = N; end
if exist('g', 'var'), values.g = g; end
if exist('a', 'var'), values.a = a; end
end

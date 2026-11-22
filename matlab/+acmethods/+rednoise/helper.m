function [retval, id] = helper(params, id)
% rednoise.helper parameters: N g a.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/rednoise.m#L44
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rednoise-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'N', 'g', 'a'}, 2, @legacyDefaults);
end

function values = legacyDefaults(N, g, a)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/rednoise.m:L44-L46
if nargin<3
    a=1;
end
%% End copied source
values = struct();
if exist('N', 'var'), values.N = N; end
if exist('g', 'var'), values.g = g; end
if exist('a', 'var'), values.a = a; end
end

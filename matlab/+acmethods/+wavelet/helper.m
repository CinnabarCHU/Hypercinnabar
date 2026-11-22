function [retval, id] = helper(params, id)
% wavelet.helper parameters: Y dt pad dj s0 J1 mother param.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wavelet.m#L96
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('wavelet-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'Y', 'dt', 'pad', 'dj', 's0', 'J1', 'mother', 'param'}, 2, @legacyDefaults);
end

function values = legacyDefaults(Y, dt, pad, dj, s0, J1, mother, param)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavelet.m:L96-L104
if (nargin < 8), param = -1;, end
if (nargin < 7), mother = -1;, end
if (nargin < 6), J1 = -1;, end
if (nargin < 5), s0 = -1;, end
if (nargin < 4), dj = -1;, end
if (nargin < 3), pad = 0;, end
if (nargin < 2)
	error('Must input a vector Y and sampling time DT')
end
%% End copied source
values = struct();
if exist('Y', 'var'), values.Y = Y; end
if exist('dt', 'var'), values.dt = dt; end
if exist('pad', 'var'), values.pad = pad; end
if exist('dj', 'var'), values.dj = dj; end
if exist('s0', 'var'), values.s0 = s0; end
if exist('J1', 'var'), values.J1 = J1; end
if exist('mother', 'var'), values.mother = mother; end
if exist('param', 'var'), values.param = param; end
end

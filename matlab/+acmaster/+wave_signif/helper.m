function [retval,id] = helper(params,id)
% wave_signif.helper parameters: Y dt scale1 sigtest lag1 siglvl dof mother param.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wave_signif.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('wave_signif-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'Y', 'dt', 'scale1', 'sigtest', 'lag1', 'siglvl', 'dof', 'mother', 'param'}, 3, @legacyDefaults);
end

function values = legacyDefaults(Y, dt, scale1, sigtest, lag1, siglvl, dof, mother, param)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wave_signif.m:L68-L76
if (nargin < 9), param = -1;, end
if (nargin < 8), mother = -1;, end
if (nargin < 7), dof = -1;, end
if (nargin < 6), siglvl = -1;, end
if (nargin < 5), lag1 = -1;, end
if (nargin < 4), sigtest = -1;, end
if (nargin < 3)
	error('Must input a vector Y, sampling time DT, and SCALE vector')
end
%% End copied source
values = struct();
if exist('Y', 'var'), values.Y = Y; end
if exist('dt', 'var'), values.dt = dt; end
if exist('scale1', 'var'), values.scale1 = scale1; end
if exist('sigtest', 'var'), values.sigtest = sigtest; end
if exist('lag1', 'var'), values.lag1 = lag1; end
if exist('siglvl', 'var'), values.siglvl = siglvl; end
if exist('dof', 'var'), values.dof = dof; end
if exist('mother', 'var'), values.mother = mother; end
if exist('param', 'var'), values.param = param; end
end

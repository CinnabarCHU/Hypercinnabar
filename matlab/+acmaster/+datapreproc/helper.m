function [retval,id] = helper(params,id)
% datapreproc.helper parameters: target qwarn.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/datapreproc.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('datapreproc-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'target', 'qwarn'}, 1, @legacyDefaults);
end

function values = legacyDefaults(target, qwarn)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/datapreproc.m:L2-L2
if nargin<2; qwarn=1; end
%% End copied source
values = struct();
if exist('target', 'var'), values.target = target; end
if exist('qwarn', 'var'), values.qwarn = qwarn; end
end

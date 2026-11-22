function [retval,id] = helper(params,id)
% zeropad2.helper parameters: data win padding.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/zeropad2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('zeropad2-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'win', 'padding'}, 1, @legacyDefaults);
end

function values = legacyDefaults(data, win, padding)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/zeropad2.m:L21-L22
if nargin < 3; padding = 1; end
if nargin < 2; win = 0.35 * abs(data(end,1) - data(1,1)); end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('win', 'var'), values.win = win; end
if exist('padding', 'var'), values.padding = padding; end
end

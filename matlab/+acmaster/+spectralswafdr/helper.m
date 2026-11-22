function [retval,id] = helper(params,id)
% spectralswafdr.helper parameters: data method nw padtimes plotn.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/spectralswafdr.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('spectralswafdr-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'method', 'nw', 'padtimes', 'plotn'}, 1, @legacyDefaults);
end

function values = legacyDefaults(data, method, nw, padtimes, plotn)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/swa/spectralswafdr.m:L30-L33
if nargin < 5; plotn = 0; end
if nargin < 4; padtimes =1; end
if nargin < 3; nw = 2; end
if nargin < 2; method = 'mtm'; end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('method', 'var'), values.method = method; end
if exist('nw', 'var'), values.nw = nw; end
if exist('padtimes', 'var'), values.padtimes = padtimes; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

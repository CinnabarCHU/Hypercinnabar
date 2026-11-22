function [retval, id] = helper(params, id)
% circularspec.helper parameters: data p1 p2 pn linlog plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/circularspec.m#L34
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('circularspec-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'p1', 'p2', 'pn', 'linlog', 'plotn'}, 1, @legacyDefaults);
end

function values = legacyDefaults(data, p1, p2, pn, linlog, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/circularspec.m:L34-L45
if nargin < 1
    errormsg('Too few input arguments');
else
    data = sort(data);
    ddf = diff(data);
    if nargin > 6; warnmsg('Too many input arguments');end
    if nargin < 6; plotn = 1; end
    if nargin < 5; linlog = 2; end
    if nargin < 4; pn = 100; end
    if nargin < 3; p2 = max(ddf)-min(ddf); end
    if nargin < 2; p1 = min(ddf); end
end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('p1', 'var'), values.p1 = p1; end
if exist('p2', 'var'), values.p2 = p2; end
if exist('pn', 'var'), values.pn = pn; end
if exist('linlog', 'var'), values.linlog = linlog; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

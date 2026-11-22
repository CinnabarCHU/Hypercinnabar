function [retval, id] = helper(params, id)
% cyclecorr.helper parameters: data targetf targetp target orbit7 rayleigh sr1 sr2 srstep sr0 adjust method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/cyclecorr.m#L27
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('cyclecorr-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'targetf', 'targetp', 'target', 'orbit7', 'rayleigh', 'sr1', 'sr2', 'srstep', 'sr0', 'adjust', 'method'}, 10, @legacyDefaults);
end

function values = legacyDefaults(data, targetf, targetp, target, orbit7, rayleigh, sr1, sr2, srstep, sr0, adjust, method)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/cyclecorr.m:L27-L37
if nargin > 12
    error('Too many input arguments in cyclecorr.m')
elseif nargin < 12
    method = 'Pearson';
    if nargin < 11
        adjust = 0;
        if nargin < 10
            error('Too few input arguments')
        end
    end
end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('targetf', 'var'), values.targetf = targetf; end
if exist('targetp', 'var'), values.targetp = targetp; end
if exist('target', 'var'), values.target = target; end
if exist('orbit7', 'var'), values.orbit7 = orbit7; end
if exist('rayleigh', 'var'), values.rayleigh = rayleigh; end
if exist('sr1', 'var'), values.sr1 = sr1; end
if exist('sr2', 'var'), values.sr2 = sr2; end
if exist('srstep', 'var'), values.srstep = srstep; end
if exist('sr0', 'var'), values.sr0 = sr0; end
if exist('adjust', 'var'), values.adjust = adjust; end
if exist('method', 'var'), values.method = method; end
end

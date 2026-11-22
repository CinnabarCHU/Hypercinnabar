function [retval, id] = helper(params, id)
% numorbit.helper parameters: orbit7 nyquist rayleigh sr_range mpts plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/numorbit.m#L23
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('numorbit-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'orbit7', 'nyquist', 'rayleigh', 'sr_range', 'mpts', 'plotn'}, 3, @legacyDefaults);
end

function values = legacyDefaults(orbit7, nyquist, rayleigh, sr_range, mpts, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/numorbit.m:L23-L39
if nargin > 6
    error('Too many input arguments')
    return;
end
if nargin < 6
    plotn = 0;
    if nargin < 5
        mpts = length(sr_range);
        if nargin < 4
            sr_range = .1:.1:20;
            if nargin < 3
                error('Too few input arguments')
                return;
            end
        end
    end
end
%% End copied source
values = struct();
if exist('orbit7', 'var'), values.orbit7 = orbit7; end
if exist('nyquist', 'var'), values.nyquist = nyquist; end
if exist('rayleigh', 'var'), values.rayleigh = rayleigh; end
if exist('sr_range', 'var'), values.sr_range = sr_range; end
if exist('mpts', 'var'), values.mpts = mpts; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

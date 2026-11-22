function [retval, id] = helper(params, id)
% redconfML.helper parameters: x dt nw nfft linlog smoothwin fmax plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redconfML.m#L44
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redconfML-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'x', 'dt', 'nw', 'nfft', 'linlog', 'smoothwin', 'fmax', 'plotn'}, 2, @legacyDefaults);
end

function values = legacyDefaults(x, dt, nw, nfft, linlog, smoothwin, fmax, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/redconfML.m:L44-L64
if nargin < 8
    plotn = 1;
    if nargin < 7
        fmax = 1/(2*dt);
    if nargin < 6
        smoothwin = 0.2;
        if nargin < 5
            linlog = 2;
            if nargin < 4
                nfft = length(x);
                if nargin < 3
                    nw = 2;
                    if nargin < 2
                        error('Error! Sampling rate is needed')
                    end
                end
            end
        end
    end
    end
end
%% End copied source
values = struct();
if exist('x', 'var'), values.x = x; end
if exist('dt', 'var'), values.dt = dt; end
if exist('nw', 'var'), values.nw = nw; end
if exist('nfft', 'var'), values.nfft = nfft; end
if exist('linlog', 'var'), values.linlog = linlog; end
if exist('smoothwin', 'var'), values.smoothwin = smoothwin; end
if exist('fmax', 'var'), values.fmax = fmax; end
if exist('plotn', 'var'), values.plotn = plotn; end
end

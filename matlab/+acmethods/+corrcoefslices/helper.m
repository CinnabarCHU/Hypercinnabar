function [retval, id] = helper(params, id)
% corrcoefslices.helper parameters: dat target orbit7 dt pad sr1 sr2 srstep adjust red nsim plotn slices.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/corrcoefslices.m#L48
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('corrcoefslices-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'dat', 'target', 'orbit7', 'dt', 'pad', 'sr1', 'sr2', 'srstep', 'adjust', 'red', 'nsim', 'plotn', 'slices'}, 3, @legacyDefaults);
end

function values = legacyDefaults(dat, target, orbit7, dt, pad, sr1, sr2, srstep, adjust, red, nsim, plotn, slices)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices.m:L48-L87
if nargin > 13
    error('Too many input arguments')
    return;
end

if nargin < 13
    slices = 1;
    if nargin < 12
    plotn = 1;
    if nargin < 11
        nsim = 0;  % no Monte Carlo simulation for confidence level estimation
        if nargin < 10
            red = 1;
            if nargin < 9
                adjust = 1;
                if nargin < 8
                    srstep = 0.2;  % sedimentation rate is 0.2 cm/kyr
                    if nargin < 7
                        sr2 = 20;   % default sed. rate from 0.1 to 20 cm/kyr
                        if nargin < 6
                            sr1 = 0.1;  % default sed. rate from 0.1 to 20 cm/kyr
                            if nargin < 5
                                pad = 5000; % zero-pading = 5000
                                if nargin < 4
                                    %dt = dat(2,1)-dat(1,1);
                                    dt = median(diff(dat(:,1)));
                                    if nargin < 3
                                        error('Too few input arguments')
                                        return;
                                    end
                                end
                            end
                        end
                    end
                end    
            end
        end
    end
    end
end
%% End copied source
values = struct();
if exist('dat', 'var'), values.dat = dat; end
if exist('target', 'var'), values.target = target; end
if exist('orbit7', 'var'), values.orbit7 = orbit7; end
if exist('dt', 'var'), values.dt = dt; end
if exist('pad', 'var'), values.pad = pad; end
if exist('sr1', 'var'), values.sr1 = sr1; end
if exist('sr2', 'var'), values.sr2 = sr2; end
if exist('srstep', 'var'), values.srstep = srstep; end
if exist('adjust', 'var'), values.adjust = adjust; end
if exist('red', 'var'), values.red = red; end
if exist('nsim', 'var'), values.nsim = nsim; end
if exist('plotn', 'var'), values.plotn = plotn; end
if exist('slices', 'var'), values.slices = slices; end
end

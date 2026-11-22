function [retval, id] = helper(params, id)
% pdan.helper parameters: data f3 window nw ftmin fterm step pad.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/pdan.m#L34
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('pdan-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'data', 'f3', 'window', 'nw', 'ftmin', 'fterm', 'step', 'pad'}, 3, @legacyDefaults);
end

function values = legacyDefaults(data, f3, window, nw, ftmin, fterm, step, pad)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/pdan.m:L34-L51
if(nargin >= 9)
    disp('>> Error: too many arguments!')
end
if(nargin < 8)
    pad = 1000;
    if nargin < 7
        step = 1;
        if nargin < 6
            fterm = 1/(2*(data(2,1)-data(1,1)));
            if nargin <5
                ftmin = 0;
                if nargin < 4
                    nw = 2;
                end
            end
        end
    end
end
%% End copied source
values = struct();
if exist('data', 'var'), values.data = data; end
if exist('f3', 'var'), values.f3 = f3; end
if exist('window', 'var'), values.window = window; end
if exist('nw', 'var'), values.nw = nw; end
if exist('ftmin', 'var'), values.ftmin = ftmin; end
if exist('fterm', 'var'), values.fterm = fterm; end
if exist('step', 'var'), values.step = step; end
if exist('pad', 'var'), values.pad = pad; end
end

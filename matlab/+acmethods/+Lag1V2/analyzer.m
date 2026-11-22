function [retval, id] = analyzer(params, id)
% Lag1V2.analyzer parameters: data window interpolate_rate padtype.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9358
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lag1V2-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
window = p.window;
interpolate_rate = p.interpolate_rate;
padtype = p.padtype;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9358-L9366
                            p = polyfit(data(:,1), data(:,2), 1);          % p(1) = slope, p(2) = intercept
                            % If you want to replace the second column in `data` with the detrended series:
                            data(:,2) = data(:,2) - polyval(p, data(:,1));

                            [data_even] = interpolate(data,interpolate_rate);
                            if padtype > 0
                                data_even = zeropad2(data_even,window,padtype);
                            end
                            [rhox] = erhoAR1(data_even,window);
%% End copied source
r = struct();
r.rhox = rhox;
r.data_even = data_even;
end

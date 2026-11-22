function [retval, id] = analyzer(params, id)
% Lag1.analyzer parameters: data window interpolate_rate.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5418
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Lag1-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
window = p.window;
interpolate_rate = p.interpolate_rate;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5418-L5419
                            [data_even] = interpolate(data,interpolate_rate);
                            [rhox] = erhoAR1(data_even,window);
%% End copied source
r = struct();
r.rhox = rhox;
end

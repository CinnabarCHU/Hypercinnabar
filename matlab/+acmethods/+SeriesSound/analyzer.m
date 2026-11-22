function [retval, id] = analyzer(params, id)
% SeriesSound.analyzer parameters: data a b c.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8606
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SeriesSound-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
a = p.a;
b = p.b;
c = p.c;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8606-L8610
                if c == 1
                    y = repmat( data(:,2)-mean(data(:,2)), [a,1]);
                else
                    y = repmat( data(:,2), [a,1]);
                end
%% End copied source
Fs=b*8192;
r = struct();
r.y = y;
r.Fs = Fs;
end

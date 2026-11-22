function [retval, id] = analyzer(params, id)
% SamplingRate.analyzer parameters: data_filterout.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5822
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SamplingRate-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5822-L5824
            t = data_filterout(:,1);
            dt = diff(t);
            len_t = length(t);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5826-L5827
            datasamp = [t(1:len_t-1),dt];
            datasamp = datasamp(~any(isnan(datasamp),2),:);
%% End copied source
r = struct();
r.datasamp = datasamp;
r.dt = dt;
end

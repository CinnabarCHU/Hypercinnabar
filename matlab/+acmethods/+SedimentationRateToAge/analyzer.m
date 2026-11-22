function [retval, id] = analyzer(params, id)
% SedimentationRateToAge.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L5044
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SedimentationRateToAge-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L5044-L5054
            data = data(~any(isnan(data),2),:);
            data = sortrows(data);
            
            time = data(:,1);
            value = data(:,2);
            npts = length(time);
            agemodel = zeros(npts,2);
            agemodel(:,1) = time;
            for i = 2:npts
                agemodel(i,2) = 100*(time(i)-time(i-1))/value(i-1)+agemodel(i-1,2);
            end
%% End copied source
r = struct();
r.agemodel = agemodel;
end

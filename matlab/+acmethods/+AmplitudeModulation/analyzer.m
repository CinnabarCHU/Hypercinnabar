function [retval, id] = analyzer(params, id)
% AmplitudeModulation.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2893
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AmplitudeModulation-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2893-L2894
            diffx = diff(data(:,1));
            if max(diffx) - min(diffx) > eps('single')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2903-L2912
                interpolate_rate = median(diffx);
                [data]=interpolate(data,interpolate_rate);
            end

            % remove mean of the 2nd column
            data(:,2) = data(:,2) - mean(data(:,2));

            % Use Hilbert transformation to extract envelope
            envelope = abs(hilbert(data(:,2)));
            data_am = [data(:,1), envelope];
%% End copied source
r = struct();
r.data_am = data_am;
end

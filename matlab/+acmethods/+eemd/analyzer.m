function [retval, id] = analyzer(params, id)
% eemd.analyzer parameters: y goal ens nos.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/eemd.m#L43
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('eemd-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
y = p.y;
goal = p.goal;
ens = p.ens;
nos = p.nos;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/eemd.m:L43-L51

% standard deviation of the input signal y is calculated
stdy = std(y);

if stdy < 0.01
    stdy = 1; % Prevent division by zero or very small standard deviation
end
y = y ./ stdy; % Normalize the signal

%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/eemd.m:L55-L56
sz = length(y); % Length of the signal
modes = zeros(goal+1, sz); % Preallocate array for modes
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/eemd.m:L73-L81
for k = 1:ens % Parallel loop for ensemble members
    disp(['Running ensemble # ', num2str(k),' / ',num2str(ens)]); % Display current ensemble number
    wn = randn(1, sz) .* nos; % Generate white noise
    y1 = y + wn; % Add noise to the signal
    y2 = y - wn; % Subtract noise from the signal
    modes = modes + emdNL(y1, goal); % Perform EMD on the noisy signal and accumulate the modes
    if nos > 0 && ens > 1
        modes = modes + emdNL(y2, goal);  % Perform EMD on the negative noisy signal and accumulate the modes
    end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/eemd.m:L92-L92
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/eemd.m:L102-L105
modes = modes .* stdy ./ (ens); % Scale back the modes and average over ensemble members
if nos > 0 && ens > 1
    modes = modes ./ 2; % Further averaging if noise is used and more than one ensemble member
end
%% End copied source
r = struct();
r.modes = modes;
end

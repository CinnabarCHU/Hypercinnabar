function [retval, id] = helper(params, id)
% EnsembleEMD.helper parameters: data_filterout.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9096
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EnsembleEMD-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
time_series=data_filterout(:,2);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9096-L9097
[imfs,~,~] = emd(time_series);
[~, ncol] = size(imfs);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9106-L9106
defaultans = {num2str(ncol+2),'100','0.2'};
%% End copied source
goal=str2double(defaultans{1}); ens=str2double(defaultans{2}); nos=str2double(defaultans{3});
r = struct();
r.data_filterout = data_filterout;
r.goal = goal;
r.ens = ens;
r.nos = nos;
end

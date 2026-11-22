function [retval, id] = analyzer(params, id)
% EnsembleEMD.analyzer parameters: data_filterout goal ens nos.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L9115
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EnsembleEMD-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
goal = p.goal;
ens = p.ens;
nos = p.nos;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8965-L8967
t = data_filterout(:,1); % first column
dt = median(diff(t)); % sampling rate
time_series = data_filterout(:,2); % 2nd column
%% End copied source
q=struct('y',time_series','goal',goal,'ens',ens,'nos',nos);
core=acmethods.eemd.analyzer(q); imfs=core.modes;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9117-L9120
    imfs = imfs';
    imfsn = size(imfs, 2);
    nw = 2;
    % plot
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9127-L9128
    pow = [];
    for k = 1:imfsn
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9137-L9140
        [po,w]=pmtm(imfs(:, k),nw);
        pow = [pow,po];
    end
    fd1=w/(2*pi*dt);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9163-L9166
    current_data = [t,imfs];
    [nrow, ncol] = size(imfs);
    imfs_var = var(imfs, 0, 1);
    total_var = sum(imfs_var);
%% End copied source
r = struct();
r.t = t;
r.time_series = time_series;
r.imfs = imfs;
r.imfsn = imfsn;
r.pow = pow;
r.fd1 = fd1;
r.current_data = current_data;
r.imfs_var = imfs_var;
r.total_var = total_var;
end

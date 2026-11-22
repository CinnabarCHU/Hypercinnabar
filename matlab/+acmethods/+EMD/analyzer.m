function [retval, id] = analyzer(params, id)
% EMD.analyzer parameters: data_filterout goal extrema intp.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8965
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EMD-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
goal = p.goal;
extrema = p.extrema;
intp = p.intp;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8965-L8967
t = data_filterout(:,1); % first column
dt = median(diff(t)); % sampling rate
time_series = data_filterout(:,2); % 2nd column
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8985-L8995
    [imfs,residual,~] = emd(time_series,'MaxNumIMF',goal,'MaxNumExtrema',extrema,'Interpolation',intp);
    imfsn = size(imfs, 2);
    nw = 2;
    pow = [];
    [po,w]=pmtm(time_series,nw);
    pow = [pow,po];
    for k = 1:imfsn
        [po,w]=pmtm(imfs(:, k),nw);
        pow = [pow,po];
    end
    fd1=w/(2*pi*dt);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L9039-L9041
    imfs_var = var(imfs, 0, 1);
    resid_var = var(residual, 0, 1);
    total_var = sum(imfs_var) + resid_var;
%% End copied source
r = struct();
r.t = t;
r.imfs = imfs;
r.residual = residual;
r.imfsn = imfsn;
r.pow = pow;
r.fd1 = fd1;
r.imfs_var = imfs_var;
r.resid_var = resid_var;
r.total_var = total_var;
end

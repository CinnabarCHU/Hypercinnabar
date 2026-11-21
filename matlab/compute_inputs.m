function q = compute_inputs(core,reference)
addpath(fullfile(core,'code','seriesanalysis'));
addpath(fullfile(core,'code','package','swa'));
addpath(fullfile(core,'code','package','wavelet'));
addpath(fullfile(core,'code','misc'));
for k=1:4
    if k<=2
        tags={'d13c','d18o'};
        raw=readmatrix(fullfile(reference,'data','Examples',['Example-cenogrid-' tags{k} '.txt']),'Delimiter',',');
    elseif k==3
        fid=fopen(fullfile(reference,'data','ZB18a.dat'),'r');
        a=textscan(fid,'%f%f%f','CommentStyle','%','CollectOutput',true); fclose(fid);
        raw=a{1}(:,1:2);
    else
        a=load(fullfile(reference,'data','La10c.mat')); raw=a.data(:,1:2);
    end
    raw=raw(raw(:,1)>=40000 & raw(:,1)<=65000,:);
    if k<=2
        dat=interpolate(raw,3.413); t=dat(:,1);
        trend=smooth(t,dat(:,2),4000/(t(end)-t(1)),'lowess');
        residual=dat(:,2)-trend; y=residual;
        lo=[55761.340,55819.361];
        y(t>=lo(k)-1e-6 & t<=55925.164+1e-6)=-0.5;
    else
        dat=raw; t=dat(:,1); trend=polyval(polyfit(t,dat(:,2),1),t);
        residual=dat(:,2)-trend; y=residual;
    end
    q(k)=struct('raw',raw,'dat',dat,'trend',trend,'residual',residual,'y',y,'t',t); %#ok<AGROW>
end
end

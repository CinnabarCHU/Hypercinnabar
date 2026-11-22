function [retval, id] = analyzer(params, id)
% DynamicFiltering.analyzer parameters: data window step fmin fmax norm padding lower upper.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/dynamic_filter_lang.m#L43
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/dynamic_filter.m#L63
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DynamicFiltering-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
window = p.window;
step = p.step;
fmin = p.fmin;
fmax = p.fmax;
norm = p.norm;
padding = p.padding;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter_lang.m:L43-L52
    time=data(:,1);
    xdata=data(:,2);
    dt = mean(diff(time)); % sampling rate
    %s=evofft18(data,window,step,dt,fmin,fmax,unit,norm,padding);
    % Bug detected. Use Acycle's version evofft with zeropad2.m function
    % ML
    % zero-padding
    [dataX] = zeropad2(data,window,padding);
    % evoFFT
    [s,x_grid,y_grid]=evofftML(dataX,window,step,fmin,fmax,norm);
%% End copied source
y_min=p.lower(:,1); x_min=p.lower(:,2);
y_max=p.upper(:,1); x_max=p.upper(:,2);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter_lang.m:L107-L108
    [y_min,I] = sort(y_min);
    x_min=x_min(I);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter.m:L68-L68
    freqboundlow = [y_min,x_min];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter.m:L87-L88
    [y_max,I] = sort(y_max);
    x_max=x_max(I);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter.m:L92-L92
    freqboundhigh = [y_max,x_max];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter_lang.m:L150-L160
    inc=step/dt;
    inc=floor(inc);
    mpts=window/dt;
    mpts=floor(mpts);
    igrid=floor(0.5*mpts);
    y_min=[y_grid(1);y_min;y_grid(end)];
    y_max=[y_grid(1);y_max;y_grid(end)];
    x_min=[x_min(1);x_min;x_min(end)];
    x_max=[x_max(1);x_max;x_max(end)];
    f_min = interp1(y_min,x_min,y_grid,'linear');
    f_max = interp1(y_max,x_max,y_grid,'linear');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter_lang.m:L166-L176
    output=zeros(length(y_grid),length(time));
    fc=zeros(length(y_grid),1);
    for n=1:length(y_grid)
        m1=max(((n*inc)-igrid),1);
        m2=min(((n*inc)+igrid),length(xdata));
        tmp_data=xdata(m1:m2);
        fc(n)=(f_min(n)+f_max(n))/2;
        %gaussbandx=gaussfilter18(tmp_data,dt,(f_min(n)+f_max(n))/2,min(f_min(n),f_max(n)),max(f_min(n),f_max(n)));
        [gaussbandx,~,~]=gaussfilter(tmp_data,dt,(f_min(n)+f_max(n))/2,min(f_min(n),f_max(n)),max(f_min(n),f_max(n)));
        output(n,m1:m2)=gaussbandx;
    end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/dynamic_filter_lang.m:L180-L181
    count=sum(output~=0,1);
    xdata_filtered=sum(output,1)./count;
%% End copied source
r = struct();
r.xdata_filtered = xdata_filtered;
r.time = time;
r.freqboundlow = freqboundlow;
r.freqboundhigh = freqboundhigh;
r.x_grid = x_grid;
r.y_grid = y_grid;
r.s = s;
r.fc = fc;
r.f_min = f_min;
r.f_max = f_max;
end

function compute_fields(profile,core,reference,dest)
% Subsample dense plots only after calculating power and significance.
if ~exist(dest,'dir'), mkdir(dest); end
rng(42025,'twister'); q=compute_inputs(core,reference);
short=ismember(profile,{'v27','v270','jan'});
for k=1:4
    z=q(k); t=z.t; y=z.y; dt=mean(diff(t)); dat=[t,y];
    out=z;
    if k<=2
        try
            evalc('sp=spectralswafdr([t,y-mean(y)],''mtm'',2,5,0);');
            out.sp=sp(:,[1 2 3 5 6 10]);
        catch err
            out.spectrum_error=err.message; fprintf('SPECTRUM %s\n',err.message);
        end
    end
    if short
        if k<=2, save(fullfile(dest,sprintf('series%d.mat',k)),'-struct','out','-v7'); end
        continue
    end
    if k<=2
        bands=[.000380 .000550;.000665 .000785];
        if k==2, bands=[.000385 .000605;.000700 .000910]; end
        for j=1:2
            b=bands(j,:); g=gaussfilter(y,dt,mean(b),b(1),b(2));
            out.g(:,j)=g(:); out.env(:,j)=abs(hilbert(g(:)));
        end
        % wave_readGUI.m, method 2. Test unrectified power before
        % applying the scale and variance corrections for display.
        [wg,wDt]=formatts(dat); n=size(wg,1); v=var(wg(:,2));
        dj=.1; s0=2*wDt; J=round(log2(n*.34*wDt/s0)/dj);
        lag=ar1nv(wg(:,2));
        [w,p,s,coi]=wavelet(wg(:,2),wDt,1,dj,s0,J,'Morlet',6);
        pw=abs(w).^2; sig=wave_signif(1,wDt,s,0,lag,-1,-1,'Morlet',6);
        jj=find(p>=58 & p<=5500); ix=unique([1:4:n n]);
        out.cwt=struct('t',wg(ix,1),'period',p(jj),'coi',coi(ix), ...
            'color',single(pw(jj,ix)./s(jj)'/v),'signif',single(pw(jj,ix)./(v*sig(jj)')), ...
            'global_power',v*mean(pw(jj,:),2)./s(jj)','lag',lag);
    end
    % PDA menu in AC.m. FFT length and integration limits use dialog defaults.
    padded=zeropad2(dat,800,1);
    try
        out.pda=pdan(padded,[1/140 1/80],800,2,0,.08,1,5000);
    catch err
        out.pda_error=err.message; fprintf('PDA %s\n',err.message);
    end
    lows=[.0003 .00028]; if k>2, lows=0; end
    for j=1:numel(lows)
        low=lows(j);
        try
            tan=tanerhilbertML(dat,(low+.0018)/2,low,.0018,1e20);
            filter_origin=profile;
        catch err
            if low~=0, rethrow(err); end
            out.native_lowpass_error=err.message;
            legacy=fullfile(fileparts(mfilename('fullpath')),'legacy');
            addpath(legacy,'-begin'); clear tanerhilbertML
            restore=onCleanup(@()rmpath(legacy));
            tan=tanerhilbertML(dat,.0009,0,.0018,1e20);
            clear restore tanerhilbertML
            filter_origin='april-legacy-zero-edge';
        end
        padded=zeropad2(tan(:,1:2),4500,1);
        [s,f,a]=evofft(padded,4500,50,dt,0,1/(2*dt),1);
        ids=f<=.0021;
        out.evo(j)=struct('low',low,'tan',tan(:,2),'f',f(ids),'age',a, ...
            'amp',single(s(:,ids)),'filter_origin',filter_origin);
    end
    save(fullfile(dest,sprintf('series%d.mat',k)),'-struct','out','-v7');
    fprintf('Saved %s series %d\n',profile,k);
end
end

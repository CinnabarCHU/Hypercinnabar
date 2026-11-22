function compare_modulators(option)
% Compare extraction of g4-g3 in the amplitudes of short eccentricity.
% All astronomical/geological inputs are public. Ages are in kyr, frequencies in cycles/Myr.
    addpath(fullfile('upstream','code','seriesanalysis'));
    if ~isfolder('outputs'),mkdir('outputs');end
    rng(150250,'twister');
    if nargin && strcmp(option,'sensitivity'),subbandSensitivity();return,end
    tb=(40010:20:64990)';
    main=[54000,62000;41000,49000;55000,61000;41000,47000;47000,52000];
    sliding=(40000:1000:57000)'; bounds=unique([main;sliding,sliding+8000],'rows','stable');
    plans=cell(size(bounds,1),1);
    for k=1:numel(plans), plans{k}=harmonicPlan(tb,bounds(k,:)); end
    for src=["ZB18a","La2010c","d13c","d18o"]
        model=any(src==["ZB18a","La2010c"]);
        if model
            a=readmatrix(fullfile('inputs',src+"_orbit_series.csv"));
        else
            a=readmatrix(fullfile('inputs',src+"_baseline_series.csv"));
        end
        t=a(:,1); x=a(:,2);
        pd=readmatrix(fullfile('inputs',src+"_80-140_pda.csv"));
        if ~model, peakAudit(src,pd(:,1),pd(:,2)); end
        full=acycleCarrier(t,x,1000/140,1000/80);
        slow=acycleCarrier(t,x,7.1,9.0);
        fast=acycleCarrier(t,x,9.25,11.4);
        vals=[bin20(pd(:,1),pd(:,2:4)),bin20(t,[full(:,3),full(:,3).^2,slow(:,3).^2,fast(:,3).^2])];
        names=["PDA_fraction","PDA_target","PDA_total","whole_AM","whole_AM_squared","slow_pair_AM_squared","fast_pair_AM_squared","paired_AM_score"];
        if model
            h=acycleCarrier(t,a(:,3),1000/75,1000/70);
            href=bin20(t,h(:,3).^2);
        end
        rows=table(); lines=table();
        for k=1:numel(plans)
            p=plans{k}; R=profile(p,vals);
            R=[R,sqrt(R(:,6).*R(:,7))];
            [power,loc]=max(R,[],1);
            freq=reshape(p.f(loc),[],1); n=numel(names); w=bounds(k,:)/1000;
            T=table(repmat(w(1),n,1),repmat(w(2),n,1),names',freq,1./freq,power', ...
                'VariableNames',{'from_Ma','to_Ma','method','frequency_cyc_Myr','period_Myr','power_or_pair_score'});
            if isempty(rows),rows=T;else,rows=[rows;T];end
            v1=lineSpacing(t,x,[7.1,9.0],bounds(k,:)); v2=lineSpacing(t,x,[9.25,11.4],bounds(k,:));
            ref=nan(1,4); refAM=NaN;
            if model
                ref=lineSpacing(t,a(:,3),[1000/78,1000/68],bounds(k,:));
                [~,im]=max(profile(p,href)); refAM=p.f(im);
            end
            T=array2table([w,v1,v2,ref,refAM], ...
                'VariableNames',{'from_Ma','to_Ma','slow_f1','slow_f2','slow_diff','slow_second_first','fast_f1','fast_f2','fast_diff','fast_second_first','h_f1','h_f2','h_diff','h_second_first','h_AM_frequency'});
            if isempty(lines),lines=T;else,lines=[lines;T];end
        end
        writetable(rows,fullfile('outputs',src+"_methods.csv"));
        writetable(lines,fullfile('outputs',src+"_line_pairs.csv"));
        if ~model
            pairedNull(src,t,[slow(:,2),fast(:,2)],plans{1},plans{2});
        end
    end
    syntheticTest();
end

function a=acycleCarrier(t,x,low,high)
    low=low/1000; high=high/1000;
    a=tanerhilbertML([t,x-mean(x)],(low+high)/2,low,high,1e20);
end

function v=bin20(t,x)
    keep=t>=40000 & t<65000; idx=floor((t(keep)-40000)/20)+1;
    z=x(keep,:); v=zeros(1250,size(z,2));
    for j=1:size(z,2), v(:,j)=accumarray(idx,z(:,j),[1250 1],@mean,NaN); end
    assert(all(isfinite(v),'all'));
end

function p=harmonicPlan(t,b)
    p.use=t>=b(1)&t<b(2); u=(t(p.use)-mean(b))/1000;
    p.sw=sqrt(hann(numel(u))); [p.tr,~]=qr(p.sw.*[ones(size(u)),u],0);
    p.f=(0.30:0.005:1.00)'; p.x=zeros(numel(p.f),numel(u)); p.y=p.x;
    for k=1:numel(p.f)
        v=p.sw.*[cos(2*pi*p.f(k)*u),sin(2*pi*p.f(k)*u)];
        [q,~]=qr(v-p.tr*(p.tr'*v),0); p.x(k,:)=q(:,1)';p.y(k,:)=q(:,2)';
    end
end

function R=profile(p,z)
    v=p.sw.*z(p.use,:); v=v-p.tr*(p.tr'*v);
    R=((p.x*v).^2+(p.y*v).^2)./sum(v.^2,1);
end

function v=lineSpacing(t,x,band,b)
    good=t>=b(1)&t<b(2); y=detrend(x(good)); dt=median(diff(t));
    [pow,f]=periodogram(y,hann(numel(y)),65536,1000/dt);
    use=f>=band(1)&f<=band(2);
    [h,loc]=findpeaks(pow(use),f(use),'SortStr','descend','MinPeakDistance',2000/diff(b));
    if numel(h)<2,v=nan(1,4);return,end
    v=[loc(1),loc(2),abs(loc(2)-loc(1)),h(2)/h(1)];
end

function y=gaussianSmooth(t,x,sigma)
    if sigma==0,y=x;return,end
    dt=median(diff(t)); k=ceil(4*sigma/dt);
    w=exp(-0.5*((-k:k)'*dt/sigma).^2);
    y=conv([repmat(x(1),k,1);x;repmat(x(end),k,1)],w/sum(w),'valid');
end

function peakAudit(src,t,x)
    use=t>=41000&t<=64000; ref=gaussianSmooth(t,x,150);
    fixed=0.1*diff(prctile(ref(use),[5,95])); out=table();
    for sigma=[0,150,250]
        v=gaussianSmooth(t,x,sigma); dynamic=0.1*diff(prctile(v(use),[5,95]));
        for mode=["relative","fixed_to_150"]
            th=dynamic; if mode=="fixed_to_150",th=fixed;end
            [mag,at,~,prom]=findpeaks(v,t,'MinPeakDistance',650,'MinPeakProminence',th);
            n=numel(at); T=table(repmat(sigma,n,1),repmat(mode,n,1),repmat(th,n,1),at/1000,mag,prom, ...
                'VariableNames',{'sigma_kyr','rule','prominence_cutoff','age_Ma','value','prominence'});
            if isempty(out),out=T;else,out=[out;T];end
        end
    end
    writetable(out,fullfile('outputs',src+"_smoothing.csv"));
    s150=ref; s250=gaussianSmooth(t,x,250); view=t>=45000 & t<=54000;
    traces=table(t(view)/1000,x(view),s150(view),s250(view), ...
        'VariableNames',{'age_Ma','PDA_fraction','smooth_150','smooth_250'});
    writetable(traces,fullfile('outputs',src+"_smoothing_traces.csv"));
    allPeaks=table();
    for sigma=[150,250]
        if sigma==150,y=s150;else,y=s250;end
        [mag,at,~,prom]=findpeaks(y,t);
        sel=at>=47000 & at<=52000; n=sum(sel);
        T=table(repmat(sigma,n,1),at(sel)/1000,mag(sel),prom(sel), ...
            'VariableNames',{'sigma_kyr','age_Ma','value','prominence'});
        if isempty(allPeaks),allPeaks=T;else,allPeaks=[allPeaks;T];end
    end
    writetable(allPeaks,fullfile('outputs',src+"_all_local_maxima.csv"));
end

function v=redistribution(p,Y)
    R=profile(p,Y); joint=sqrt(R(:,1).*R(:,2));
    short=p.f>=1/1.6 & p.f<=1/1.2; long=p.f>=1/2.6 & p.f<=1/2.0;
    v=log(mean(joint(short))/mean(joint(long)));
end

function pairedNull(src,t,realCarriers,old,young)
    % Random common phase at each Fourier frequency, preserving the full
    % stationary auto/cross spectra of both filtered bands. Primary statistic
    % tests temporal redistribution of the shared subband modulation.
    n=numel(t); spec=fft(realCarriers); pos=(2:floor((n+1)/2))';
    B=399; out=zeros(B+1,3);
    for j=1:B+1
        if j==1, y=realCarriers;
        else
            u=spec; u(pos,:)=spec(pos,:).*exp(2i*pi*rand(numel(pos),1));
            u(n-pos+2,:)=conj(u(pos,:)); y=real(ifft(u));
        end
        env=bin20(t,abs(hilbert(y)).^2);
        a=redistribution(old,env); b=redistribution(young,env); out(j,:)=[a,b,a-b];
    end
    writetable(array2table(out,'VariableNames',{'old_log_short_long','young_log_short_long','old_minus_young'}),fullfile('outputs',src+"_paired_change.csv"));
    fprintf('SPLIT %s observed=%.5f p_one_sided=%.5f\n',src,out(1,3),(1+sum(out(2:end,3)>=out(1,3)))/(B+1));
end

function syntheticTest()
    t=(0:5:19200)'; P=1600; slow=cos(2*pi*t/P); carrier=cos(2*pi*t/100);
    background=cos(2*pi*t/41); amp=1+.45*slow; width=800;
    signals=[amp.*carrier,carrier+amp.*background];
    for j=1:2
        a=acycleCarrier(t,signals(:,j),1000/140,1000/80);
        en(:,j)=a(:,3).^2;
    end
    % Call original historical PDA with the settings matching the archived figures.
    addpath(fullfile('legacy','code','seriesanalysis'),'-begin');
    assert(contains(which('pdan'),[filesep 'legacy' filesep]));
    vars=["PDA_fraction","PDA_target","PDA_total","whole_AM_squared"]; out=table();
    for j=1:2
        cases=["100k_am_only","constant_100k_plus_41k_am"];
        pd=pdan([t,signals(:,j)],[1/140,1/80],width,2,0,0.08,2,5000);
        tk=pd(:,1); vk=[pd(:,2:4),interp1(t,en(:,j),tk)];
        use=tk>=1600 & tk<17600; phase=2*pi*tk(use)/P; 
        X=[ones(size(phase)),cos(phase),sin(phase),cos(2*phase),sin(2*phase)];
        beta=X\vk(use,:); C=beta(2,:)./beta(1,:); S=beta(3,:)./beta(1,:);
        T=table(repmat(cases(j),4,1),vars',C',S',hypot(C,S)', ...
           'VariableNames',{'case_name','estimate','inphase_over_mean','quadrature_over_mean','fractional_semiamplitude'});
        if isempty(out),out=T;else,out=[out;T];end
    end
    writetable(out,fullfile('outputs','synthetic_denominator.csv')); disp(out);
end


function subbandSensitivity()
    % Perturb the same two families of short-eccentricity lines. Evaluate
    % each variant and one common statistic (median over the 18 variants).
    bands=[7.10 9.00 9.25 11.40; 7.25 8.75 9.45 11.15; 6.90 9.10 9.15 11.65];
    windows=[54000 62000 41000 49000;55000 61000 41000 47000;54000 60000 42000 48000];
    tbin=(40010:20:64990)'; po=cell(3,1);py=po;
    for w=1:3
        po{w}=harmonicPlan(tbin,windows(w,1:2));py{w}=harmonicPlan(tbin,windows(w,3:4));
    end
    rng(35895,'twister'); B=399;
    for src=["d13c","d18o"]
        raw=readmatrix(fullfile('inputs',src+"_baseline_series.csv"));t=raw(:,1);v=raw(:,2);
        signals=zeros(numel(t),6);
        for b=1:3
            c=acycleCarrier(t,v,bands(b,1),bands(b,2));d=acycleCarrier(t,v,bands(b,3),bands(b,4));
            signals(:,2*b-1:2*b)=[c(:,2),d(:,2)];
        end
        spec=fft(signals); n=numel(t);pos=(2:floor((n+1)/2))';
        out=zeros(B+1,18); ids=zeros(18,3);
        for j=1:B+1
            if j==1,y=signals;
            else
                u=spec;u(pos,:)=spec(pos,:).*exp(2i*pi*rand(numel(pos),1));
                u(n-pos+2,:)=conj(u(pos,:));y=real(ifft(u));
            end
            A=abs(hilbert(y));both=bin20(t,[A,A.^2]);m=0;
            for w=1:3
                old=profile(po{w},both); young=profile(py{w},both);
                f=po{w}.f; short=f>=1/1.6 & f<=1/1.2;long=f>=1/2.6 & f<=1/2.0;
                for power=1:2
                    for b=1:3
                        idx=(power-1)*6+(2*b-1:2*b);
                        vo=sqrt(prod(old(:,idx),2));vy=sqrt(prod(young(:,idx),2));
                        m=m+1;ids(m,:)=[w,power,b];
                        out(j,m)=log(mean(vo(short))/mean(vo(long)))-log(mean(vy(short))/mean(vy(long)));
                    end
                end
            end
        end
        med=median(out,2);obs=out(1,:);p=(1+sum(out(2:end,:)>=obs,1))/(B+1);
        summary=array2table([windows(ids(:,1),:)/1000,ids(:,2),bands(ids(:,3),:),obs',p'], ...
          'VariableNames',{'old_start_Ma','old_end_Ma','young_start_Ma','young_end_Ma','envelope_power','slow_low','slow_high','fast_low','fast_high','log_contrast','conditional_p'});
        writetable(summary,fullfile('outputs',src+"_method_sensitivity.csv"));
        writematrix(med,fullfile('outputs',src+"_median_surrogates.csv"));
        fprintf('GRID %s contrast_min_median_max=[%.4f %.4f %.4f] p_median=%.4f individual_p_range=[%.4f %.4f]\n', ...
            src,min(obs),med(1),max(obs),(1+sum(med(2:end)>=med(1)))/(B+1),min(p),max(p));
    end
end

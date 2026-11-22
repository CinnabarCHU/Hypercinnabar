function carrier_controls()
% Check the two-window spectral redistribution under time-dependent proxy
% gain, event treatment, and age-matched single-site sampling.
    addpath(fullfile('upstream','code','seriesanalysis')); mkdir('model-output');
    rng(516410,'twister'); results=table(); calib=table(); folds=table();
    site=readmatrix(fullfile('inputs','1209.csv'));[st,~,group]=unique(site(:,1));
    siteVals=[accumarray(group,site(:,2),[],@mean),accumarray(group,site(:,3),[],@mean)];
    centers=(40010:20:64990)'; main=[54000,62000;41000,49000];
    compare=[55000,61000;46000,52000];
    for j=1:2
        names=["d13c","d18o"];src=names(j);
        a=readmatrix(fullfile('inputs',src+"_baseline_series.csv")); t=a(:,1);x=a(:,2);
        sig=carriers(t,x); E=bin(t,abs(hilbert(sig)).^2,centers);
        base=twoPlans(centers,main,true(size(centers)));
        [row,~]=obs(src,"CENOGRID","usual",base,E); results=add(results,row);
        % Remove the entire PETM and neighboring samples from scoring on the
        % existing envelopes. A separate replacement before filtering checks ringing.
        valid=~(centers>=55150 & centers<=56450);
        p=twoPlans(centers,main,valid);[row,~]=obs(src,"CENOGRID","mask_55.15_56.45",p,E);results=add(results,row);
        replace=t>=55700&t<=55980;
        v=x;L=median(x(t>=55550&t<55700));R=median(x(t>55980&t<=56130));
        v(replace)=interp1([55700;55980],[L;R],t(replace));
        eb=bin(t,abs(hilbert(carriers(t,v))).^2,centers);[row,~]=obs(src,"CENOGRID","alternative_PETM_bridge",base,eb);results=add(results,row);
        if src=="d13c"
            raw=readmatrix(fullfile('inputs','raw_cenogrid_d13c.csv'),'Delimiter',',');
            raw=raw(raw(:,1)>=40000 & raw(:,1)<=65000,:); uni=interpolate(raw,3.413);
            assert(max(abs(uni(:,1)-t))<1e-4);
            ramp=min(1,max(0,(51600-t)/600));
            for amp=[0,.5,1]
                v=uni(:,2)-amp*ramp;v=v-smooth(t,v,4000/range(t),'lowess');
                v(t>=55761.340-1e-5 & t<=55925.164+1e-5)=-.5;
                if amp==0,assert(norm(v-x)/norm(x)<1e-5);continue,end
                eb=bin(t,abs(hilbert(carriers(t,v))).^2,centers);
                [row,~]=obs(src,"CENOGRID","background_ramp_"+string(amp),base,eb);results=add(results,row);
            end
        end
        % Retain the long-term, band-specific standard deviations but shake
        % the standardized carriers' phases. The same Fourier phase at each
        % bin is used for both bands so their residual cross-spectrum is preserved.
        for w=[0,1000,2000,3000]
            if w==0,s=ones(size(sig));else,s=localGain(sig,t,w);end
            scaled=sig./s;sp=fft(scaled);n=numel(t);pos=(2:floor((n+1)/2))';
            B=799;Z=zeros(B+1,1);
            for k=1:B+1
                if k==1,val=E;
                else
                    u=sp;u(pos,:)=sp(pos,:).*exp(2i*pi*rand(numel(pos),1));u(n-pos+2,:)=conj(u(pos,:));
                    randomized=s.*real(ifft(u));val=bin(t,abs(hilbert(randomized)).^2,centers);
                end
                [~,o]=summaryPower(base{1},val);[~,y]=summaryPower(base{2},val);Z(k)=o-y;
            end
            pv=(1+sum(Z(2:end)>=Z(1)))/(B+1);
            rr=table(src,w/1000,Z(1),pv,B,'VariableNames',{'isotope','gain_sigma_Myr','delta_observed','empirical_p','surrogates'});
            calib=add(calib,rr);writematrix(Z,fullfile('model-output',src+"_gain"+string(w)+"_null.csv"));
        end
        % Test whether the Pacific record and the splice in the same windows
        % have the same direction. Match age coverage, then additionally match
        % sample geometry. Compensation for effects of gaps remains approximate.
        use=st>=45000&st<=65000 & st>=min(t)&st<=max(t);
        ss=st(use);vv=siteVals(use,j); new=interpolate([ss,vv],5);
        ts=new(:,1);vs=new(:,2)-smoothdata(new(:,2),'lowess',801);
        siteE=bin(ts,abs(hilbert(carriers(ts,vs))).^2,centers);
        cn=interp1(t,x,ss);samp=interpolate([ss,cn],5);
        assert(isequal(samp(:,1),ts));
        sampledE=bin(ts,abs(hilbert(carriers(ts,samp(:,2)))).^2,centers);
        ok=true(size(centers)); gaps=find(diff(ss)>50);
        for idx=gaps',ok(centers>=ss(idx)-200 & centers<=ss(idx+1)+200)=false;end
        for mask=["all","gap_mask"]
            take=true(size(centers));if mask=="gap_mask",take=ok;end
            p=twoPlans(centers,compare,take);
            for index=1:3
                labels=["CENOGRID","CENOGRID_at_1209_ages","Site1209"];
                if index==1,v=E;elseif index==2,v=sampledE;else,v=siteE;end
                [row,~]=obs(src,labels(index),mask,p,v);results=add(results,row);
            end
        end
        % Report sensitivity to either end of the long-window estimate.
        for wo={[55000,61000;41000,47000],[54000,60000;42000,48000]}
            p=twoPlans(centers,wo{1},true(size(centers)));
            [row,~]=obs(src,"CENOGRID","6_Myr",p,E);folds=add(folds,row);
        end
    end
    writetable(results,fullfile('model-output','record_checks.csv'));writetable(calib,fullfile('model-output','gain_nulls.csv'));
    writetable(folds,fullfile('model-output','short_windows.csv')); disp(calib);disp(results(:,[1:3,10:14]));
end

function T=add(T,row)
    if isempty(T),T=row;else,T=[T;row];end
end

function Y=carriers(t,x)
    b=[7.1,9;9.25,11.4]/1000;Y=zeros(numel(t),2);
    for j=1:2
        q=tanerhilbertML([t,x-mean(x)],mean(b(j,:)),b(j,1),b(j,2),1e20);
        Y(:,j)=q(:,2);
    end
end

function s=localGain(y,t,width)
    dt=median(diff(t));n=numel(t);h=min(n-1,ceil(4*width/dt));
    w=exp(-.5*((-h:h)'*dt/width).^2);w=w/sum(w);
    padded=[flipud(y(2:h+1,:));y;flipud(y(end-h:end-1,:))].^2;
    s=sqrt(conv2(padded,w,'valid'));s=max(s,eps);
end

function out=bin(t,x,c)
    v=t>=c(1)-10 & t<c(end)+10;
    ix=floor((t(v)-(c(1)-10))/20)+1; ix=min(ix,numel(c));
    out=nan(numel(c),size(x,2));
    for k=1:size(x,2),out(:,k)=accumarray(ix,x(v,k),[numel(c),1],@mean,NaN);end
end

function pp=twoPlans(c,b,mask)
    pp={make(c,b(1,:),mask),make(c,b(2,:),mask)};
end

function p=make(t,b,mask)
    inside=t>=b(1)&t<b(2);p.use=inside&mask;p.cover=sum(p.use)/sum(inside);p.range=b/1000;
    u=(t(p.use)-mean(b))/1000;
    % Match the discrete symmetric Hann of the previous unmasked window.
    fullH=hann(sum(inside));tmp=zeros(size(t));tmp(inside)=fullH;w=sqrt(tmp(p.use));
    p.w=w;[p.q,~]=qr(w.*[ones(size(u)),u],0);
    p.f=(.30:.005:1.0)'; p.x=zeros(numel(p.f),numel(u));p.y=p.x;
    for k=1:numel(p.f)
        V=w.*[cos(2*pi*p.f(k)*u),sin(2*pi*p.f(k)*u)];
        [v,~]=qr(V-p.q*(p.q'*V),0);p.x(k,:)=v(:,1)';p.y(k,:)=v(:,2)';
    end
end

function [period,ratio]=summaryPower(p,E)
    z=p.w.*E(p.use,:);assert(all(isfinite(z),'all'));z=z-p.q*(p.q'*z);
    R=((p.x*z).^2+(p.y*z).^2)./sum(z.^2,1);G=sqrt(prod(R,2));
    short=p.f>=1/1.6 & p.f<=1/1.2;long=p.f>=1/2.6 & p.f<=1/2;
    [~,i]=max(G);period=1/p.f(i);ratio=log(mean(G(short))/mean(G(long)));
end

function [row,z]=obs(src,record,choice,p,E)
    [op,a]=summaryPower(p{1},E);[yp,b]=summaryPower(p{2},E);z=a-b;
    w=[p{1}.range,p{2}.range];
    row=table(src,record,choice,w(1),w(2),w(3),w(4),p{1}.cover,p{2}.cover,op,yp,exp(a),exp(b),z, ...
        'VariableNames',{'isotope','record','choice','old_min_Ma','old_max_Ma','young_min_Ma','young_max_Ma','old_coverage','young_coverage','old_peak_Myr','young_peak_Myr','old_short_long','young_short_long','log_contrast'});
end

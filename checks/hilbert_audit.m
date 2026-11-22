function hilbert_audit()
% All filter estimates and hypothesis tests run in MATLAB on GitHub Actions.
% Ages in the raw files are kyr BP, reporting frequencies in cycles/Myr.
    addpath(fullfile('upstream','code','seriesanalysis'));
    mkdir('audit-output'); rng(734128,'twister');
    bands=[1000/45,1000/35;7.10,9.00;9.25,11.40];
    synthetic_check(bands);
    carrierPSD=table(); extraCarriers=cell(1,3);
    age=(40.01:.02:64.99)'; gridF=unique([(.30:.005:1)';2/3]);
    windows=[54,62;41,49;55,61;54,60;46.6,51.6];
    plans=cell(size(windows,1),1);
    for j=1:numel(plans), plans{j}=makeplan(age,windows(j,:),gridF);end
    freqTilt=(.30:.01:2.0)';
    prof=table(); scores=table(); tiltres=table(); quality=table();
    baseEnvelope=table(age,'VariableNames',{'age_Ma'});
    conditions=["main_q20","default_q12","q6","reflect_2Myr","narrow_pairs","wide_pairs","retain_PETM","bridge_PETM"];
    for j=1:2
        if j==1, src="d13c";startPETM=55761.340;else,src="d18o";startPETM=55819.361;end
        raw=readmatrix("inputs/"+src+"_raw.txt",'Delimiter',',');
        raw=raw(raw(:,1)>=40000 & raw(:,1)<=65000,:);
        xx=interpolate(raw,3.413);t=xx(:,1); x0=xx(:,2)-smooth(t,xx(:,2),4000/range(t),'lowess');
        x=x0;x(t>=startPETM-1e-5&t<=55925.164+1e-5)=-.5;
        B=binner(t); ref=table(t/1000,x,'VariableNames',{'age_Ma','input'});
        bandNames=["tilt","slow","fast"];
        for mode=conditions
            q=20; b=bands; sig=x; mirror=0;
            switch mode
                case "default_q12",q=NaN;
                case "q6",q=6;
                case "reflect_2Myr",mirror=2000;
                case "narrow_pairs",b(2:3,:)=[7.25,8.75;9.45,11.15];
                case "wide_pairs",b(2:3,:)=[6.90,9.10;9.15,11.65];
                case "retain_PETM",sig=x0;
                case "bridge_PETM"
                    sig=x0;cut=t>=55700&t<=55980;
                    endpoints=[median(x0(t>=55550&t<55700));median(x0(t>55980&t<=56130))];
                    sig(cut)=interp1([55700;55980],endpoints,t(cut));
            end
            F=zeros(numel(t),3);E=F;
            for k=1:3
                z=channel(t,sig,b(k,:),q,mirror);F(:,k)=z(:,2);E(:,k)=z(:,3);
                if mode=="main_q20"
                    ref.(bandNames(k))=F(:,k);ref.(bandNames(k)+"_A")=E(:,k);
                end
            end
            if mode=="main_q20" || mode=="retain_PETM" || mode=="bridge_PETM"
                ind=find(["main_q20","retain_PETM","bridge_PETM"]==mode);
                extraCarriers{ind}(:,2*j-1:2*j)=F(:,2:3);
            end
            amp=B*E(:,1); pair=B*(E(:,2:3).^2);
            if mode=="main_q20"
                baseF=F;carrierPSD=[carrierPSD;tilt_psd(src,t,sig,F(:,1))];
                nullInput(:,2*j-1:2*j)=F(:,2:3); %#ok<AGROW>
                baseEnvelope.(src+"_tilt_A")=amp;baseEnvelope.(src+"_slow_A2")=pair(:,1);baseEnvelope.(src+"_fast_A2")=pair(:,2);
                writetable(ref,"audit-output/"+src+"_native.csv");
            end
            for w=1:numel(plans)
                bounds=windows(w,:);p=plans{w};
                R=evaluate(p,pair);J=sqrt(prod(R,2));[val,ii]=max(J);
                [~,ind]=max(R,[],1); k=find(abs(gridF-2/3)<1e-12);
                a=age(p.use);u=a-mean(bounds);v=pair(p.use,:);
                skill=NaN;if w<=2,skill=cv(u,v,a,bounds,2/3);end
                scores=[scores;table(src,mode,bounds(1),bounds(2),1/gridF(ii),val,1/gridF(ind(1)),1/gridF(ind(2)),R(k,1),R(k,2),J(k),skill, ...
                    'VariableNames',{'source','setting','from_Ma','to_Ma','free_joint_period','free_joint','free_slow_period','free_fast_period','exact15_slow_R2','exact15_fast_R2','exact15_joint','exact15_CV'})]; %#ok<AGROW>
                if w<=2
                    z=evaluate(makeplan(age,bounds,freqTilt),amp);[best,li]=max(z);
                    tiltres=[tiltres;table(src,mode,bounds(1),bounds(2),1/freqTilt(li),best,...
                        'VariableNames',{'source','setting','from_Ma','to_Ma','free_tilt_A_period','free_tilt_R2'})]; %#ok<AGROW>
                    sel=t>=1000*bounds(1)&t<1000*bounds(2);
                    for bn=1:3
                        y=F(sel,bn);[pow,fr]=periodogram(y,hann(numel(y)),65536,1000/median(diff(t)));
                        [~,ix]=max(pow);rel=norm(y-baseF(sel,bn))/norm(baseF(sel,bn));
                        quality=[quality;table(src,mode,bandNames(bn),bounds(1),bounds(2),1000/fr(ix),rel,...
                            'VariableNames',{'source','setting','band','from_Ma','to_Ma','strongest_carrier_kyr','relative_RMS_change'})]; %#ok<AGROW>
                    end
                end
                if mode=="main_q20"
                    rawR=evaluate(p,B*sig);n=numel(gridF);
                    prof=[prof;table(repmat(src,n,1),repmat(bounds(1),n,1),repmat(bounds(2),n,1),gridF,R(:,1),R(:,2),J,rawR,...
                        'VariableNames',{'source','from_Ma','to_Ma','frequency','slow_R2','fast_R2','joint','proxy_direct_R2'})]; %#ok<AGROW>
                end
            end
        end
    end
    writetable(scores,'audit-output/parameter_sensitivity.csv');writetable(tiltres,'audit-output/tilt_sensitivity.csv');
    writetable(quality,'audit-output/carrier_diagnostics.csv');writetable(prof,'audit-output/profiles.csv');
    writetable(baseEnvelope,'audit-output/envelopes.csv');
    orbitP=orbit_diagnostic(bands);writetable([carrierPSD;orbitP],'audit-output/tilt_carrier_PSD.csv');
    phase_test(t,B,nullInput,plans{1},gridF);
    local_variance_test(t,B,age,extraCarriers);
end

function out=channel(t,x,band,q,padding)
    band=band/1000;dt=median(diff(t));m=round(padding/dt);
    if m>0
        x=[flipud(x(2:m+1));x;flipud(x(end-m:end-1))];
        t=t(1)+(-m:numel(t)-1+m)'*dt;
    end
    args={[t,x-mean(x)],mean(band),band(1),band(2)};
    if isfinite(q),args{end+1}=10^q;end
    out=tanerhilbertML(args{:});
    if m>0,out=out(m+1:end-m,:);end
end

function B=binner(t)
    idx=find(t>=40000&t<65000);g=floor((t(idx)-40000)/20)+1;
    counts=accumarray(g,1,[1250,1]);assert(all(counts>0));
    B=sparse(g,idx,1./counts(g),1250,numel(t));
end

function p=makeplan(age,bounds,f)
    p.use=age>=bounds(1)&age<bounds(2);u=age(p.use)-mean(bounds);
    p.w=sqrt(hann(numel(u)));[p.tr,~]=qr(p.w.*[ones(size(u)),u],0);
    p.c=zeros(numel(f),numel(u));p.s=p.c;
    for k=1:numel(f)
        D=p.w.*[cos(2*pi*f(k)*u),sin(2*pi*f(k)*u)];
        [Q,~]=qr(D-p.tr*(p.tr'*D),0);p.c(k,:)=Q(:,1)';p.s(k,:)=Q(:,2)';
    end
end

function R=evaluate(p,y)
    y=p.w.*y(p.use,:); y=y-p.tr*(p.tr'*y);
    R=((p.c*y).^2+(p.s*y).^2)./sum(y.^2,1);
end

function skill=cv(u,v,a,bounds,f)
    X0=[ones(size(u)),u]; X=[X0,cos(2*pi*f*u),sin(2*pi*f*u)];s0=0;s1=0;
    for left=bounds(1):bounds(2)-1
        te=a>=left&a<left+1;tr=a<left-1|a>=left+2;
        d0=X0(tr,:)\v(tr,:);d=X(tr,:)\v(tr,:);
        scale=sqrt(mean((v(tr,:)-X0(tr,:)*d0).^2,1));
        s0=s0+sum(((v(te,:)-X0(te,:)*d0)./scale).^2,'all');s1=s1+sum(((v(te,:)-X(te,:)*d)./scale).^2,'all');
    end
    skill=1-s1/s0;
end

function synthetic_check(bands)
    t=(0:5:23995)';u=t/1000;labels=["tilt","slow","fast"];f1=[25,8,10];res=table();gains=table();
    for b=1:3
        fs=[f1(b),f1(b)+2/3,16];phi=[.3,-.7,1.3];w=[1,.6,.75];
        V=cos(2*pi*u*fs+phi);x=V*w';edge=bands(b,:)/1000;
        for q=[6,12,20]
            [out,~,~,h,f]=tanerhilbertML([t,x],mean(edge),edge(1),edge(2),10^q);
            ix=round(fs*24)+1;couple=w.*reshape(h(ix),1,[]);
            expected=V*couple';expectedA=abs(exp(1i*(2*pi*u*fs+phi))*couple');
            noArg=channel(t,x,bands(b,:),NaN,0);asMa=tanerhilbertML([u,x],1000*mean(edge),1000*edge(1),1000*edge(2),10^q);
            [p,fr]=periodogram(out(:,3).^2-mean(out(:,3).^2),[],numel(t),1000/5);
            [~,i]=max(p);err=max(abs(out(:,2)-expected));errA=max(abs(out(:,3)-expectedA));
            assert(err<1e-10 && errA<1e-10 && abs(fr(i)-2/3)<1e-8);
            res=[res;table(labels(b),q,err,errA,1/fr(i),max(abs(asMa(:,2)-out(:,2))),max(abs(noArg(:,2)-out(:,2))), ...
                'VariableNames',{'band','q','carrier_max_error','envelope_max_error','recovered_beat_Myr','kyr_Ma_max_error','vs_default_max_error'})]; %#ok<AGROW>
            sel=f*1000<=40;n=sum(sel);
            gains=[gains;table(repmat(labels(b),n,1),repmat(q,n,1),f(sel)*1000,h(sel), ...
                'VariableNames',{'band','q','frequency','gain'})]; %#ok<AGROW>
        end
    end
    writetable(res,'audit-output/synthetic.csv');writetable(gains,'audit-output/response.csv');
end

function pp=orbit_diagnostic(bands)
    t=(38000:5:67000)';
    pt=readmatrix('inputs/PT.dat','FileType','text');tilt=interp1(-pt(:,1),pt(:,2),t);
    fid=fopen('inputs/ems-plan3.dat');assert(fid>=0);
    for k=1:3,fgetl(fid);end
    z=textscan(fid,repmat('%f',1,8),'CommentStyle','#','CollectOutput',true);fclose(fid);z=z{1};
    e=interp1(-z(:,1)/365250,z(:,3),t);
    O=table(t/1000,'VariableNames',{'age_Ma'});
    names=["tilt","slow","fast"];
    for k=1:3
        if k==1,x=tilt;else,x=e;end
        a=channel(t,x,bands(k,:),20,0);O.(names(k))=a(:,2);O.(names(k)+"_A")=a(:,3);
    end
    writetable(O,'audit-output/ZB18a_native.csv');pp=tilt_psd("ZB18a",t,tilt,O.tilt);
end

function phase_test(t,B,Y,p,f)
% Preserve exact stationary auto- and cross-spectra of four filtered carriers
% with a common random phase at every positive Fourier bin. Test both the
% prespecified period and the maximum after scanning f=.30 to 1.00 cycles/Myr.
    N=numel(t);pos=(2:floor((N+1)/2))';S=fft(Y);reps=1999;
    tests=zeros(reps+1,4);exact=find(abs(f-2/3)<1e-12);
    for k=1:reps+1
        if k==1,car=Y;else
            U=S;U(pos,:)=S(pos,:).*exp(2i*pi*rand(numel(pos),1));U(N-pos+2,:)=conj(U(pos,:));car=real(ifft(U));
        end
        R=evaluate(p,B*(abs(hilbert(car)).^2));
        J=[sqrt(R(:,1).*R(:,2)),sqrt(R(:,3).*R(:,4))];
        tests(k,:)=[J(exact,:),max(J,[],1)];
    end
    writetable(array2table(tests,'VariableNames',{'C_exact','O_exact','C_scan','O_scan'}),'audit-output/phase_draws.csv');
    labels=["d13c","d18o"];out=table();
    for j=1:2
        exactP=(1+sum(tests(2:end,j)>=tests(1,j)))/(reps+1);
        searchP=(1+sum(tests(2:end,j+2)>=tests(1,j+2)))/(reps+1);
        eitherP=(1+sum(max(tests(2:end,1:2),[],2)>=tests(1,j)))/(reps+1);
        fullP=(1+sum(max(tests(2:end,3:4),[],2)>=tests(1,j+2)))/(reps+1);
        out=[out;table(labels(j),reps,tests(1,j),exactP,eitherP,tests(1,j+2),searchP,fullP, ...
            'VariableNames',{'source','surrogates','J_exact','p_fixed','p_fixed_either_proxy','J_scan','p_scan','p_scan_either_proxy'})]; %#ok<AGROW>
    end
    writetable(out,'audit-output/phase_tests.csv');disp(out);
end

function out=tilt_psd(src,t,x,filtered)
    out=table();bounds=[54 62;41 49];
    for j=1:2
        b=bounds(j,:); sel=t>=1000*b(1)&t<1000*b(2);w=hann(sum(sel));
        [pow,f]=periodogram(detrend([x(sel),filtered(sel)]),w,32768,1000/median(diff(t)));
        keep=f>=20&f<=31;n=sum(keep);
        out=[out;table(repmat(src,n,1),repmat(b(1),n,1),repmat(b(2),n,1),f(keep),pow(keep,1),pow(keep,2), ...
            'VariableNames',{'source','from_Ma','to_Ma','frequency','unfiltered_density','filtered_density'})]; %#ok<AGROW>
    end
end

function local_variance_test(t,B,age,carriers)
% Compare a fixed period, frequencies read from ZB18a/La2010c h on the
% identical window, and an average of J over the approximate prediction.
    optional=(1/1.6:.005:1/1.4)';optional(end+1)=1/1.4;
    f=unique([2/3;.6317138671875;.4913330078125;optional]);
    indexes=ismember(f,optional);p=makeplan(age,[54,62],f);
    n=numel(t);pos=(2:floor((n+1)/2))';
    reps=1999; names=["main_q20","retain_PETM","bridge_PETM"]; labs=["d13c","d18o"]; out=table();
    for v=1:3
        for width=[0 2000]
            rng(734128,'twister');Y=carriers{v};gain=ones(size(Y));
            if width>0
                h=min(n-1,ceil(4*width/median(diff(t))));
                w=exp(-.5*((-h:h)'*median(diff(t))/width).^2);w=w/sum(w);
                padded=[flipud(Y(2:h+1,:));Y;flipud(Y(end-h:end-1,:))];
                gain=sqrt(conv2(padded.^2,w,'valid'));assert(all(gain>0,'all'));
            end
            S=fft(Y./gain);stats=zeros(reps+1,2,4);
            for k=1:reps+1
                if k==1,y=Y;else
                    U=S;U(pos,:)=S(pos,:).*exp(2i*pi*rand(numel(pos),1));U(n-pos+2,:)=conj(U(pos,:));
                    y=real(ifft(U)).*gain;
                end
                R=evaluate(p,B*abs(hilbert(y)).^2);
                J=[sqrt(prod(R(:,1:2),2)),sqrt(prod(R(:,3:4),2))];
                stats(k,:,1)=J(f==2/3,:);stats(k,:,2)=J(f==.6317138671875,:);
                stats(k,:,3)=J(f==.4913330078125,:);
                stats(k,:,4)=trapz(f(indexes),J(indexes,:))/(max(f(indexes))-min(f(indexes)));
            end
            measures=["exact_1p50","ZB_h_1p583","La_h_2p035","mean_1p40_1p60"];
            for m=1:4
                for j=1:2
                    obs=stats(1,j,m);single=(1+sum(stats(2:end,j,m)>=obs))/(reps+1);
                    both=(1+sum(max(stats(2:end,:,m),[],2)>=obs))/(reps+1);
                    out=[out;table(labs(j),names(v),width,measures(m),reps,obs,single,both, ...
                        'VariableNames',{'source','setting','gain_sigma_kyr','test','N_surrogates','joint','p_record','p_either_record'})]; %#ok<AGROW>
                end
            end
        end
    end
    writetable(out,'audit-output/variance_nulls.csv');
end

function obliquity_test()
% Track the free Hilbert-amplitude peak of the obliquity carrier on published ages.
% Ages in the imported tables are kyr BP. Spectral frequencies are cycles/Myr.
    addpath(fullfile('upstream','code','seriesanalysis'));
    mkdir('tilt-output');
    rng(543182,'twister');
    [o,c,orbitTime,nodalEnvelope]=public_series();
    age = (40010:20:64990)'/1000;
    windows = [54,62;41,49;55,61;41,47;54,60;42,48];
    f = (.30:.01:2.00)';
    centers = (44:.2:61)';
    mainPlans = cell(size(windows,1),1);
    movingPlans = cell(numel(centers),1);
    for w=1:size(windows,1), mainPlans{w}=make_plan(age,windows(w,:),f); end
    for w=1:numel(centers), movingPlans{w}=make_plan(age,centers(w)+[-4,4],f); end

    pt = readmatrix('inputs/PT.dat','FileType','text');
    tilt = interp1(-pt(:,1),pt(:,2),orbitTime);
    t = o(:,1); assert(isequal(t,c(:,1)));
    labels = ["ZB_tilt","oxygen","carbon","ZB_grid","ZB_at_O_ages","ZB_at_C_ages"];
    ts = {orbitTime,t,t,t}; uniform = interp1(orbitTime,tilt,t);
    values = {tilt,o(:,2),c(:,2),uniform}; cadence = table();
    for iso = ["d18o","d13c"]
        raw = readmatrix("inputs/"+iso+"_raw.txt",'Delimiter',',');
        samples = unique(raw(all(isfinite(raw(:,1:2)),2),1));
        samples = samples(samples>=min(t)-200 & samples<=max(t)+200);
        x = interp1(orbitTime,tilt,samples);
        assert(all(isfinite(x)));
        values{end+1} = interp1(samples,x,t,'linear','extrap'); ts{end+1}=t;
        for k=1:2
            lim=windows(k,:); sel=samples>=1000*lim(1) & samples<1000*lim(2);
            step=diff(samples(sel));
            cadence=[cadence;table(iso,lim(1),lim(2),sum(sel),median(step),max(step),sum(step>20),...
                'VariableNames',{'isotope','from_Ma','to_Ma','sample_ages','median_gap_kyr','max_gap_kyr','gaps_over_20_kyr'})]; %#ok<AGROW>
        end
    end
    writetable(cadence,'tilt-output/sampling.csv');
    env = table(age,'VariableNames',{'age_Ma'});
    % The long beat is read independently from the nodal variable p in both solutions.
    nodal=binner(orbitTime)*nodalEnvelope; solLabels=["ZB_p","La_p"];
    allSources = [labels,solLabels]; profiles=table(); slides=table(); sensitivity=table();
    ref=zeros(size(windows,1),2);
    for w=1:size(windows,1)
        R=profile(mainPlans{w},nodal);
        [~,peak]=max(R,[],1);ref(w,:)=reshape(f(peak),1,2);
    end
    edges=[1000/45,1000/35;1000/48,1000/33;24,27.5]; % cycles/Myr
    realCarrier=zeros(numel(t),2); sampledTilt=zeros(numel(t),2);
    for j=1:numel(allSources)
        name=allSources(j);
        if j<=numel(labels)
            tj=ts{j}; xj=values{j}; nb=3;
            bin=binner(tj);
        else
            nb=1;
        end
        for b=1:nb
            if j<=numel(labels)
                out=channel(tj,xj,edges(b,:)); A=out(:,3);
                if b==1
                    if j==2 || j==3
                        realCarrier(:,j-1)=out(:,2);
                    elseif j==5 || j==6
                        sampledTilt(:,j-4)=out(:,2);
                    end
                end
                curves=[bin*A,bin*(A.^2)];
            else
                curves=nodal(:,j-numel(labels));
            end
            for pow=1:size(curves,2)
                e=curves(:,pow);
                if b==1 && pow==1
                    env.(name)=e;
                    pieces=cell(numel(centers),1);
                    for m=1:numel(centers)
                        r=profile(movingPlans{m},e); n=numel(f);
                        pieces{m}=table(repmat(name,n,1),repmat(centers(m),n,1),f,r,...
                            'VariableNames',{'source','center_Ma','frequency','partial_R2'});
                    end
                    slides=[slides;vertcat(pieces{:})]; %#ok<AGROW>
                end
                for w=1:size(windows,1)
                    p=mainPlans{w}; r=profile(p,e);
                    [best,ix]=max(r); tz=nearest(f,ref(w,1)); tl=nearest(f,ref(w,2));
                    bounds=windows(w,:); span=diff(bounds);
                    [cvZ,cvL]=deal(NaN);
                    if b==1 && pow==1 && w<=2
                        cvZ=predict_window(age,e,bounds,f(tz));
                        cvL=predict_window(age,e,bounds,f(tl));
                    end
                    row=table(name,b,pow,bounds(1),bounds(2),f(ix),1/f(ix),best,...
                        f(tz),r(tz),f(tl),r(tl),cvZ,cvL,abs(f(ix)-f(tz))<=1/span,...
                        'VariableNames',{'source','band','envelope_power','from_Ma','to_Ma','free_frequency','free_period','free_R2','ZB_frequency','ZB_R2','La_frequency','La_R2','ZB_skill','La_skill','within_one_Rayleigh_ZB'});
                    sensitivity=[sensitivity;row]; %#ok<AGROW>
                    if b==1 && pow==1 && w<=2
                        n=numel(f); row=table(repmat(name,n,1),repmat(bounds(1),n,1),repmat(bounds(2),n,1),f,r,...
                            'VariableNames',{'source','from_Ma','to_Ma','frequency','partial_R2'});
                        profiles=[profiles;row]; %#ok<AGROW>
                    end
                end
            end
        end
    end
    writetable(profiles,'tilt-output/endpoint_profiles.csv'); writetable(sensitivity,'tilt-output/band_sensitivity.csv');
    writetable(slides,'tilt-output/moving_profiles.csv'); writetable(env,'tilt-output/amplitude_series.csv');
    simulate_background(t,realCarrier,sampledTilt,binner(t),mainPlans(1:2),ref(1:2,:),f);
end

function [o,c,t,nodalEnvelope]=public_series()
% Rebuild the archived proxy preprocessing and nodal envelopes directly
% from the pinned Acycle examples and the two public orbital integrations.
    for name=["d18o","d13c"]
        raw=readmatrix("inputs/"+name+"_raw.txt",'Delimiter',',');
        raw=raw(raw(:,1)>=40000 & raw(:,1)<=65000,:);
        regridded=interpolate(raw,3.413);t=regridded(:,1);x=regridded(:,2);
        x=x-smooth(t,x,4000/range(t),'lowess');
        if name=="d18o", startPETM=55819.361;else,startPETM=55761.340;end
        x(t>=startPETM-1e-5 & t<=55925.164+1e-5)=-.5;
        if name=="d18o", o=[t,x];else,c=[t,x];end
    end
    t=(38000:5:67000)';
    fid=fopen('inputs/ems-plan3.dat');assert(fid>=0);
    for i=1:3, fgetl(fid);end
    data=textscan(fid,repmat('%f',1,8),'CommentStyle','#','CollectOutput',true);fclose(fid);
    z=data{1};pn=interp1(-z(:,1)/365250,sind(z(:,4)/2).*sind(z(:,6)),t);
    l=readmatrix('inputs/La2010c.dat','FileType','text');
    nodes=[pn,interp1(-l(:,1),l(:,7),t)]; assert(all(isfinite(nodes),'all'));
    nodalEnvelope=zeros(size(nodes));
    for j=1:2
        a=channel(t,nodes(:,j),[1000/74,1000/68]);
        nodalEnvelope(:,j)=a(:,3);
    end
end

function q=channel(t,x,band)
    b=band/1000;
    q=tanerhilbertML([t,x-mean(x)],mean(b),b(1),b(2),1e20);
end

function B=binner(t)
    use=find(t>=40000 & t<65000);
    group=floor((t(use)-40000)/20)+1; n=1250;
    counts=accumarray(group,1,[n,1]);assert(all(counts>0));
    B=sparse(group,use,1./counts(group),n,numel(t));
end

function p=make_plan(age,bounds,f)
    p.use=age>=bounds(1)&age<bounds(2);u=age(p.use)-mean(bounds);
    p.w=sqrt(hann(numel(u)));[p.q,~]=qr(p.w.*[ones(size(u)),u],0);
    p.c=zeros(numel(f),numel(u));p.s=p.c;
    for k=1:numel(f)
        D=p.w.*[cos(2*pi*f(k)*u),sin(2*pi*f(k)*u)];
        [q,~]=qr(D-p.q*(p.q'*D),0);p.c(k,:)=q(:,1)';p.s(k,:)=q(:,2)';
    end
end

function r=profile(p,E)
    y=p.w.*E(p.use,:);y=y-p.q*(p.q'*y);
    r=((p.c*y).^2+(p.s*y).^2)./sum(y.^2,1);
end

function i=nearest(f,target)
    [~,i]=min(abs(f-target));
end

function skill=predict_window(age,e,b,frequency)
% Hold out each successive Myr. The fit to envelope phase and amplitude is
% restricted to its own window, with one Myr of guard on each side.
    use=age>=b(1) & age<b(2); a=age(use);u=a-mean(b);y=e(use);
    trend=[ones(size(a)),u];X=[trend,cos(2*pi*frequency*u),sin(2*pi*frequency*u)];
    s0=0;s1=0;
    for left=b(1):b(2)-1
        test=a>=left & a<left+1;train=a<left-1 | a>=left+2;
        pred0=trend(test,:)*(trend(train,:)\y(train));pred1=X(test,:)*(X(train,:)\y(train));
        s0=s0+sum((y(test)-pred0).^2);s1=s1+sum((y(test)-pred1).^2);
    end
    skill=1-s1/s0;
end

function simulate_background(t,carrier,tilt,bin,plans,targets,f)
% Randomize the phase of each Fourier bin after normalizing the broad
% envelope gain. The same random rotation is applied to O and C per bin.
    half=min(numel(t)-1,ceil(8000/median(diff(t))));
    kernel=exp(-.5*((-half:half)'*median(diff(t))/2000).^2);kernel=kernel/sum(kernel);
    extended=[flipud(carrier(2:half+1,:));carrier;flipud(carrier(end-half:end-1,:))];
    gain=sqrt(conv2(extended.^2,kernel,'valid'));gain=max(gain,eps);n=numel(t);
    spectrum=fft(carrier./gain);pos=(2:floor((n+1)/2))';
    lambda=[0,.25,.5,.75,1,1.5,2]; B=599;
    % Injection sizes are RMS ratios of the narrowband carrier over 40-65 Ma.
    tilt=hilbert(tilt)./sqrt(mean(tilt.^2,1));
    hit=zeros(B,numel(lambda),2,3); tg=zeros(B+1,2,2,3); % ZB, La, frequency-scan maximum
    for i=0:B
        if i==0
            noise=carrier;
        else
            v=spectrum;v(pos,:)=spectrum(pos,:).*exp(2i*pi*rand(numel(pos),1));v(n-pos+2,:)=conj(v(pos,:));
            noise=gain.*real(ifft(v));
        end
        z=hilbert(noise);
        plain=bin*abs(z);
        for w=1:2
            r=profile(plans{w},plain);
            for sol=1:2
                tg(i+1,:,w,sol)=r(nearest(f,targets(w,sol)),:);
            end
            tg(i+1,:,w,3)=max(r,[],1);
        end
        if i==0,continue,end
        % Uniform carrier phase, common to both isotope experiments. The
        % orbital amplitude envelope keeps its geologic age orientation.
        signal=tilt.*sqrt(mean(noise.^2,1))*exp(2i*pi*rand);
        E=zeros(size(bin,1),2*numel(lambda));
        for k=1:numel(lambda)
            E(:,2*k-1:2*k)=bin*abs(z+lambda(k)*signal);
        end
        both=true(2,numel(lambda));
        for w=1:2
            r=profile(plans{w},E); [~,index]=max(r,[],1);
            recovered=reshape(abs(f(index)-targets(w,1))<=.125,2,[]);
            for j=1:2,hit(i,:,j,w)=recovered(j,:);end
            both=both & recovered;
        end
        for j=1:2,hit(i,:,j,3)=both(j,:);end
    end
    species=["oxygen","carbon"]; stats=table(); sensitivity=table(); draws=table();
    for j=1:2
        for sol=1:3
            key=["ZB_fixed","La_fixed","free_max"];
            for w=1:3
                if w<3
                    v=squeeze(tg(:,j,w,sol));
                else
                    v=sqrt(tg(:,j,1,sol).*tg(:,j,2,sol));v=v(:);
                end
                empirical=(1+sum(v(2:end)>=v(1)))/(B+1);
                groups=["old","young","both"]; kind=groups(w);method=key(sol);
                stats=[stats;table(species(j),kind,method,v(1),empirical,prctile(v(2:end),95),B,...
                    'VariableNames',{'source','window','method','observed','empirical_p','null_q95','replicates'})]; %#ok<AGROW>
                draws.(species(j)+"_"+kind+"_"+method)=v;
            end
        end
        for w=1:3
            groups=["old","young","both"]; n=numel(lambda);rate=squeeze(mean(hit(:,:,j,w),1));
            sensitivity=[sensitivity;table(repmat(species(j),n,1),repmat(groups(w),n,1),lambda',rate(:),repmat(B,n,1),...
                'VariableNames',{'background','window','injected_over_background_RMS','recovery_fraction','replicates'})]; %#ok<AGROW>
        end
    end
    writetable(stats,'tilt-output/null_summary.csv'); writetable(draws,'tilt-output/null_draws.csv');
    writetable(sensitivity,'tilt-output/injection_recovery.csv');
end

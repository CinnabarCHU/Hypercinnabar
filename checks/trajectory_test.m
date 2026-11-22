function trajectory_test()
% Compare predictions of the modulation envelopes, conditional on the
% published chronology. All ages are Ma, increasing into the past.
    addpath(fullfile('upstream','code','seriesanalysis'));
    mkdir('model-output'); rng(4153,'twister');
    ages=(41.025:0.05:62.975)'; Y=[]; names=strings(1,0);
    for src=["ZB18a","La2010c","d13c","d18o"]
        if any(src==["ZB18a","La2010c"]),file=src+"_orbit_series.csv";
        else,file=src+"_baseline_series.csv";end
        a=readmatrix(fullfile('inputs',file));
        [A,E]=extract(a(:,1)/1000,a(:,2)); Y=[Y,E,A]; names=[names,src+"_energy",src+"_amplitude"];
    end
    % Known mechanisms share endpoint frequencies and transition geometry.
    % Each noise realization is reused across mechanisms.
    t=(38:0.005:67)'; [u,phi]=phaseRamp(t,[.405,.665,50.5,5.5]);
    fy=.405; fo=.665;
    for r=0:3
        noise=zeros(size(t)); 
        if r>0
            for carrier=[8.05,10.325]
                coef=exp(-.005/.18); q=filter(sqrt(1-coef^2),[1,-coef],randn(numel(t),2));
                noise=noise+.19*(q(:,1).*cos(2*pi*carrier*t)+q(:,2).*sin(2*pi*carrier*t));
            end
        end
        for planted=["drift","mixture"]
            x=noise; 
            for j=1:2
                centers=[8.05,10.325]; offsets=[.4,-.7]; off=offsets(j);
                if planted=="drift"
                    mod=(1-.2*u).*cos(phi+off);
                else
                    mod=(1-u).*cos(2*pi*fy*(t-41)+off)+.8*u.*cos(2*pi*fo*(t-41)+off+1.3);
                end
                x=x+sqrt(1+.52*mod).*cos(2*pi*centers(j)*t+.25*j);
            end
            [~,E]=extract(t,x);Y=[Y,E];names=[names,"known_"+planted+"_"+string(r)];
        end
    end
    wm=table(); predictions=table(); envelopeTable=array2table([ages,Y], ...
        'VariableNames',["age_Ma",reshape([names+"_slow";names+"_fast"],1,[])]);
    writetable(envelopeTable,fullfile('model-output','envelopes.csv'));
    % Only three fixed interior knots are used for changing background level.
    N=[ones(size(ages)),(ages-52)/5.5,max(0,(ages-[46.5,52,57.5])/5.5)];
    for fold=0:11
        if fold==0, train=true(size(ages)); test=true(size(ages));lo=41;hi=63;
        else, lo=41+2*(fold-1);hi=lo+2;test=ages>=lo & ages<hi;
            train=ages<lo-1 | ages>=hi+1;end
        nTr=N(train,:); r=Y(train,:)-nTr*(nTr\Y(train,:));scale=sqrt(mean(r.^2,1));
        [Q,~]=qr(nTr,0); z=r./scale;
        [pars,gain]=searchModels(ages(train),Q,z);
        for g=1:numel(names)
            cols=[2*g-1,2*g];
            basePred=N(test,:)*(nTr\Y(train,cols));
            err0=((Y(test,cols)-basePred)./scale(cols)).^2;
            for m=1:3
                prm=reshape(pars(m,g,:),1,4); X=carrierDesign(ages,prm,m);
                V=[N,X]; co=V(train,:)\Y(train,cols);pred=V(test,:)*co;
                err=((Y(test,cols)-pred)./scale(cols)).^2;
                method=["constant","drift","mixture"]; lab=method(m);
                row=table(names(g),fold,lo,hi,lab,prm(1),prm(2),prm(3),prm(4),sum(err0,'all'),sum(err,'all'),gain(m,g), ...
                    'VariableNames',{'series','fold','from_Ma','to_Ma','model','young_frequency','old_frequency','transition_center','transition_width','sse_background','sse_model','training_gain'});
                if isempty(wm),wm=row;else,wm=[wm;row];end
                if fold>0 && ~startsWith(names(g),"known")
                    n=sum(test);cur=table(repmat(names(g),n,1),repmat(lab,n,1),repmat(fold,n,1),ages(test), ...
                        Y(test,cols(1)),Y(test,cols(2)),pred(:,1),pred(:,2),basePred(:,1),basePred(:,2), ...
                        'VariableNames',{'series','model','fold','age_Ma','observed_slow','observed_fast','predicted_slow','predicted_fast','background_slow','background_fast'});
                    if isempty(predictions),predictions=cur;else,predictions=[predictions;cur];end
                end
            end
        end
        fprintf('Completed age block %d\n',fold);
    end
    writetable(wm,fullfile('model-output','heldout_fits.csv'));
    writetable(predictions,fullfile('model-output','heldout_predictions.csv'));
    result=table();
    for g=1:numel(names)
        for region=["all","47_53"]
            v=wm(wm.series==names(g) & wm.fold>0,:);
            if region=="47_53",v=v(v.from_Ma>=47 & v.to_Ma<=53,:);end
            skill=zeros(1,3);method=["constant","drift","mixture"];
            for m=1:3
                r=v(v.model==method(m),:);skill(m)=1-sum(r.sse_model)/sum(r.sse_background);
            end
            rr=table(names(g),region,skill(1),skill(2),skill(3),skill(2)-skill(3), ...
                'VariableNames',{'series','evaluation_region','constant_skill','drift_skill','mixture_skill','drift_minus_mixture'});
            if isempty(result),result=rr;else,result=[result;rr];end
        end
    end
    writetable(result,fullfile('model-output','predictive_skill.csv'));
    disp(result(result.evaluation_region=="all",:));
    % Estimate squared energy in the analytic filter's impulse response
    % outside the one-Myr train/test buffer. This is conditional validation
    % of already filtered envelopes, not wholly independent observations.
    t=(0:.005:40)'; x=zeros(size(t));[~,center]=min(abs(t-20));x(center)=1;
    bc=[7.10,9.0;9.25,11.4]; tails=zeros(2,3);
    for j=1:2
        p=band(t,x,bc(j,:));v=p(:,3).^2;
        tails(j,:)=[bc(j,:),sum(v(abs(t-20)>1))/sum(v)];
    end
    writematrix(tails,fullfile('model-output','analytic_filter_tail.csv'));
end

function [A,E]=extract(t,x)
    b=[7.10,9;9.25,11.4];good=t>=41 & t<63; ix=floor((t(good)-41)/.05)+1;
    ix=min(ix,440);A=zeros(440,2); E=A;
    for j=1:2
        p=band(t,x,b(j,:)); y=p(good,3);
        A(:,j)=accumarray(ix,y,[440,1],@mean,NaN);
        E(:,j)=accumarray(ix,y.^2,[440,1],@mean,NaN);
    end
    assert(all(isfinite([A,E]),'all'));
end

function p=band(t,x,b)
    % Acycle sees kyr and cycles/kyr, as in the published-data comparison.
    p=tanerhilbertML([1000*t,x-mean(x)],mean(b)/1000,b(1)/1000,b(2)/1000,1e20);
end

function [u,phase]=phaseRamp(t,p)
    a=p(3)-p(4)/2;b=p(3)+p(4)/2;
    u=min(1,max(0,(t-a)/p(4)));
    integral=(max(t-a,0).^2-max(t-b,0).^2)/(2*p(4));
    phase=2*pi*(p(1)*(t-41)+(p(2)-p(1))*integral);
end

function X=carrierDesign(t,p,m)
    if m==1, a=2*pi*p(1)*(t-41);X=[cos(a),sin(a)];return,end
    [u,phase]=phaseRamp(t,p);
    if m==2,a=phase;b=phase;else,a=2*pi*p(1)*(t-41);b=2*pi*p(2)*(t-41);end
    X=[(1-u).*cos(a),(1-u).*sin(a),u.*cos(b),u.*sin(b)];
end

function g=gainAt(t,Q,z,p,m)
    X=carrierDesign(t,p,m);X=X-Q*(Q'*X);[q,r]=qr(X,0);
    if min(abs(diag(r)))<1e-8, g=-Inf(1,size(z,2)/2);return,end
    a=sum((q'*z).^2,1);g=a(1:2:end)+a(2:2:end);
end

function [pars,best]=searchModels(t,Q,z)
    groups=size(z,2)/2;best=-inf(3,groups);pars=zeros(3,groups,4);
    f=.30:.05:1.0;
    for fy=f
        p=[fy,fy,50,5];v=gainAt(t,Q,z,p,1); hit=v>best(1,:);
        if any(hit),best(1,hit)=v(hit);pars(1,hit,:)=repmat(reshape(p,1,1,4),1,sum(hit),1);end
        for fo=f
            for c=[46,48,50,52,54]
                for d=[2,5,8]
                    p=[fy,fo,c,d];
                    for m=2:3
                        v=gainAt(t,Q,z,p,m);hit=v>best(m,:);
                        if any(hit),best(m,hit)=v(hit);pars(m,hit,:)=repmat(reshape(p,1,1,4),1,sum(hit),1);end
                    end
                end
            end
        end
    end
    opt=optimset('Display','off','MaxFunEvals',180,'MaxIter',150,'TolX',1e-5,'TolFun',1e-6);
    for g=1:groups
        zz=z(:,[2*g-1,2*g]); f0=pars(1,g,1);
        fn=@(f)-gainAt(t,Q,zz,[f,f,50,5],1);
        [ff,v]=fminbnd(fn,max(.30,f0-.05),min(1.0,f0+.05),opt);
        if -v>best(1,g),pars(1,g,1:2)=reshape([ff,ff],1,1,2);best(1,g)=-v;end
        for m=2:3
            start=reshape(pars(m,g,:),1,4);
            [p,v]=fminsearch(@(p)objective(p,t,Q,zz,m),start,opt);
            if -v>best(m,g),pars(m,g,:)=reshape(p,1,1,4);best(m,g)=-v;end
        end
    end
end

function v=objective(p,t,Q,z,m)
    low=[.30,.30,45,1];high=[1,1,56,10];
    if any(p<low|p>high),v=1e4+sum(max(0,low-p).^2+max(0,p-high).^2);return,end
    v=-gainAt(t,Q,z,p,m);
end

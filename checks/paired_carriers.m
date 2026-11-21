function paired_carriers()
% Paired AM frequency diagnostics on already published ages. Time increases
% into the past. These are envelope/line diagnostics, not resonant angles.
    addpath(fullfile('upstream','code','seriesanalysis'));
    mkdir('paired'); rng(120926,'twister');
    win=[54000,62000; 41000,49000; 55000,61000; 41000,47000; 54000,60000; 42000,48000];
    % First pair maximizes resolution within the composite. Alternate pairs
    % restrict the potential influence of a time-varying transition.
    for name=["d13c","d18o"]
        a=readmatrix(fullfile('inputs',name+"_baseline_series.csv"));
        s=channel(a(:,1),a(:,2),35,45); g=channel(a(:,1),a(:,2),80,140);
        assert(norm(s(:,3)-a(:,4))/norm(a(:,4))<1e-7);
        assert(norm(g(:,3)-a(:,3))/norm(a(:,3))<1e-7);
        comparePairs(name,"standard",a(:,1),g(:,3),s(:,3),win);
        comparePairs(name,"wide",a(:,1),a(:,5),a(:,6),win);
        linePair(name,a(:,1),a(:,2),[35,45],win);
        conditionalNull(name,a(:,1),g(:,2),s(:,2),win(1:2,:));
    end
    for name=["ZB18a","La2010c"]
        a=readmatrix(fullfile('inputs',name+"_orbit_series.csv"));
        comparePairs(name,"h_p",a(:,1),a(:,6),a(:,7),win);
        linePair(name+"_h",a(:,1),a(:,3),[68,78],win);
        linePair(name+"_p",a(:,1),a(:,4),[65,77],win);
        if name=="ZB18a"
            tmp=readmatrix(fullfile('inputs','PT.dat'),'FileType','text');
            tilt=interp1(-tmp(:,1),tmp(:,2),a(:,1));
            direct=channel(a(:,1),tilt,35,45);
            comparePairs(name,"e_tilt",a(:,1),a(:,5),direct(:,3),win);
            s=channel(a(:,1),tilt,33,48); g=channel(a(:,1),a(:,2),75,150);
            comparePairs(name,"e_tilt_wide",a(:,1),g(:,3),s(:,3),win);
            linePair(name+"_tilt",a(:,1),tilt,[35,45],win);
        end
    end
    a=readmatrix(fullfile('inputs','1209.csv'));
    [age,~,grp]=unique(a(:,1));
    % Use complete pairs for both isotopes; duplicate ages are averaged.
    % Only old windows have the same duration and coverage as the composite.
    siteWin=[win(1:2:end,:); 46000,52000];
    for j=2:3
        name=["1209d13c","1209d18o"]; name=name(j-1);
        val=accumarray(grp,a(:,j),[],@mean);
        v=interpolate([age,val],5);
        dt=median(diff(v(:,1))); sm=round(4000/dt); y=v(:,2)-smoothdata(v(:,2),'lowess',sm);
        g=channel(v(:,1),y,80,140); s=channel(v(:,1),y,35,45);
        comparePairs(name,"site",v(:,1),g(:,3),s(:,3),siteWin);
        linePair(name,v(:,1),y,[35,45],siteWin);
        irregularLines(name,age,val,siteWin);
    end
end

function v=channel(t,x,pmin,pmax)
    lo=1/pmax; hi=1/pmin;
    v=tanerhilbertML([t(:),x(:)-mean(x)],(lo+hi)/2,lo,hi,1e20);
end

function comparePairs(name,method,t,g,s,win)
    M=zeros(size(win,1),11);
    for j=1:size(win,1)
        plan=makePlan(t,win(j,:)); M(j,:)=[win(j,:)/1000,score(plan,g,s)];
    end
    vars={'from_Ma','to_Ma','free_g_cyc_Myr','free_s_cyc_Myr','free_s_over_g','max_fraction_g','max_fraction_s','score_1','score_2','joint_g1','joint_g2'};
    writetable(array2table(M,'VariableNames',vars),fullfile('paired',name+"_"+method+"_am.csv"));
    fprintf('PAIRS %s %s old_young\n',name,method); disp(M(1:min(2,end),[1:5,8,9]));
end

function p=makePlan(t,b)
    % Bin into 20-kyr cells for envelope analysis, Hann-weighted removal of
    % linear trend, harmonic regression on the same weighted residuals.
    edges=(b(1):20:b(2))'; p.use=t>=b(1) & t<b(2);
    p.group=discretize(t(p.use),edges); centers=(edges(1:end-1)+10)/1000;
    p.n=numel(centers); x=centers-mean(centers); w=hann(p.n);
    p.sw=sqrt(w); design=p.sw.*[ones(size(x)),x];
    [p.trend,~]=qr(design,0);
    p.f=(0.30:0.01:2.00)'; p.gidx=find(p.f<=1.00001);
    p.g2idx=round((2*p.f(p.gidx)-p.f(1))/0.01)+1;
    % Two orthonormal sine/cosine columns per frequency, with intercept
    % and slope projected out. Squared projections are partial R-squared.
    p.cos=zeros(numel(p.f),p.n); p.sin=p.cos;
    for k=1:numel(p.f)
        A=p.sw.*[cos(2*pi*p.f(k)*x),sin(2*pi*p.f(k)*x)];
        [Q,~]=qr(A-p.trend*(p.trend'*A),0);
        p.cos(k,:)=Q(:,1)'; p.sin(k,:)=Q(:,2)';
    end
end

function v=score(p,g,s)
    wave=[accumarray(p.group,g(p.use),[p.n,1],@mean),accumarray(p.group,s(p.use),[p.n,1],@mean)];
    V=p.sw.*wave; V=V-p.trend*(p.trend'*V);
    power=((p.cos*V).^2+(p.sin*V).^2)./sum(V.^2,1);
    [rg,k]=max(power(p.gidx,1)); fg=p.f(p.gidx(k));
    [rs,k]=max(power(:,2)); fs=p.f(k);
    % Geometric mean requires both carriers to contribute to a common relation.
    [s1,k1]=max(sqrt(power(p.gidx,1).*power(p.gidx,2)));
    [s2,k2]=max(sqrt(power(p.gidx,1).*power(p.g2idx,2)));
    v=[fg,fs,fs/fg,rg,rs,s1,s2,p.f(p.gidx(k1)),p.f(p.gidx(k2))];
end

function conditionalNull(name,t,g,s,win)
    old=makePlan(t,win(1,:)); young=makePlan(t,win(2,:));
    pairs=[g(:),s(:)]; spectra=fft(pairs); n=size(pairs,1);
    idx=(2:floor((n+1)/2))'; B=399; out=zeros(B+1,3);
    for b=1:B+1
        if b==1
            full=pairs;
        else
            f=spectra;
            f(idx,:)=abs(spectra(idx,:)).*exp(2i*pi*rand(numel(idx),2));
            f(n-idx+2,:)=conj(f(idx,:)); full=real(ifft(f));
        end
        env=abs(hilbert(full));
        o=score(old,env(:,1),env(:,2)); y=score(young,env(:,1),env(:,2));
        do=o(7)-o(6); dy=y(7)-y(6); out(b,:)=[do,dy,dy-do];
    end
    p=(1+sum(out(2:end,3)>=out(1,3)))/(B+1);
    fprintf('NULL %s B=%d old_d=%.5f young_d=%.5f change=%.5f one_sided_p=%.4f\n',name,B,out(1,:),p);
    writetable(array2table(out,'VariableNames',{'old_S2_minus_S1','young_S2_minus_S1','change'}), ...
        fullfile('paired',name+"_null.csv"));
end

function linePair(name,t,y,pband,win)
    M=zeros(size(win,1),7); dt=median(diff(t));
    for i=1:size(win,1)
        bounds=win(i,:); sel=t>=bounds(1) & t<bounds(2); x=detrend(y(sel));
        [d,f]=periodogram(x,hann(numel(x)),65536,1000/dt);
        M(i,:)=[bounds/1000,pickLines(d,f,pband,2000/diff(bounds))];
    end
    saveLines(name,M);
end

function irregularLines(name,t,y,win)
    % Nonuniform, unfilled Site 1209 data. Linear detrending and Hann
    % weights on real sample ages; orthogonalized two-column harmonic fit.
    M=zeros(size(win,1),7);
    for i=1:size(win,1)
        b=win(i,:); use=t>=b(1) & t<b(2); u=(t(use)-mean(b))/1000;
        w=sqrt(0.5+0.5*cos(2*pi*u/(diff(b)/1000))); [q,~]=qr(w.*[ones(size(u)),u],0);
        r=w.*y(use); r=r-q*(q'*r); f=(1000/45:0.01:1000/35)'; d=zeros(size(f));
        for k=1:numel(f)
            A=w.*[cos(2*pi*f(k)*u),sin(2*pi*f(k)*u)]; [v,~]=qr(A-q*(q'*A),0);
            d(k)=sum((v'*r).^2)/sum(r.^2);
        end
        M(i,:)=[b/1000,pickLines(d,f,[35,45],2000/diff(b))];
        fprintf('SITE %s %.0f %.0f n=%d med_gap_kyr=%.2f max_gap_kyr=%.2f\n',name,b,numel(u),median(diff(t(use))),max(diff(t(use))));
    end
    saveLines(name+"_irregular",M);
end

function v=pickLines(d,f,band,minsep)
    ids=f>=1000/band(2) & f<=1000/band(1);
    [p,loc]=findpeaks(d(ids),f(ids),'SortStr','descend','MinPeakDistance',minsep);
    if numel(p)<2, v=nan(1,5); return, end
    sep=abs(diff(loc(1:2)));
    v=[loc(1),loc(2),sep,1/sep,p(2)/p(1)];
end

function saveLines(name,M)
    vars={'from_Ma','to_Ma','primary_cyc_Myr','secondary_cyc_Myr','difference_cyc_Myr','beat_Myr','second_over_first_power'};
    writetable(array2table(M,'VariableNames',vars),fullfile('paired',name+"_doublets.csv"));
end

function modulation_check(task)
% Sensitivity calculations on openly published CENOGRID and orbital solutions.
% Ages throughout the calculation increase into the past, in kyr.
    root = fullfile(pwd,'upstream','code');
    addpath(fullfile(root,'seriesanalysis'),fullfile(root,'package','swa'), ...
            fullfile(root,'package','wavelet'));
    mkdir('results');
    rng(52640,'twister');
    if strcmp(task,'orbit')
        orbitalChecks();
    else
        isotopeChecks(string(task));
    end
end

function isotopeChecks(name)
    raw = readmatrix(fullfile('upstream','data','Examples', ...
        "Example-cenogrid-"+name+".txt"),'Delimiter',',');
    raw = raw(raw(:,1)>=40000 & raw(:,1)<=65000,:);
    uniform = interpolate(raw,3.413);
    t = uniform(:,1);
    event = t>=55761.340-1e-5 & t<=55925.164+1e-5;
    cases = ["baseline","half","full","smoothfull"];
    if name=="d18o"
        event = t>=55819.361-1e-5 & t<=55925.164+1e-5;
        cases = "baseline";
    end
    fprintf('INPUT %s rows=%d range=%.6f:%.6f event=%d\n', ...
        name,numel(t),t(1),t(end),sum(event));
    for scenario = cases
        ramp = min(1,max(0,(51600-t)/600));
        switch scenario
            case "baseline", amplitude = 0;
            case "half", amplitude = 0.5;
            case "full", amplitude = 1;
            case "smoothfull", amplitude = 1; ramp = ramp.^2.*(3-2*ramp);
        end
        corrected = uniform(:,2)-amplitude*ramp;
        y = corrected-smooth(t,corrected,4000/range(t),'lowess');
        y(event) = -0.5;
        prefix = name+"_"+scenario;
        d = diagnostics(t,y); emit(prefix,"direct",d);
        a100 = carrier(t,y,80,140);
        d100 = diagnostics(t,a100(:,3)); emit(prefix,"AM80_140",d100);
        near = t>=50000 & t<=53000;
        if scenario=="baseline"
            baseline = d;
            referenceEnvelope = a100(:,3);
            refNear = mean(referenceEnvelope(near).^2);
        end
        fprintf('RAMP %s shortPowerOverBase=%.7f longPowerOverBase=%.7f carrierRmsRelativeDifference=%.7f carrierMeanSquareOverBase=%.7f\n', ...
            prefix,d.localShort/baseline.localShort,d.localLong/baseline.localLong, ...
            norm(a100(near,3)-referenceEnvelope(near))/norm(referenceEnvelope(near)), ...
            mean(a100(near,3).^2)/refNear);
        if scenario=="smoothfull", continue, end
        % Same GUI compatibility function and padding, not the strict new PDA.
        padded = zeropad2([t,y],800,1);
        pd = pdan(padded,[1/140,1/80],800,2,0,1/(2*mean(diff(t))),1,5000);
        writematrix(pd,fullfile('results',prefix+"_pda.csv"));
        dRel = diagnostics(pd(:,1),pd(:,2)); emit(prefix,"PDAfraction",dRel);
        dAbs = diagnostics(pd(:,1),pd(:,3)); emit(prefix,"PDAband",dAbs);
        middle = pd(:,1)>=47000 & pd(:,1)<=52000;
        r = corrcoef(pd(middle,2),pd(middle,3));
        local = pd(:,1)>=50000 & pd(:,1)<=53000;
        if scenario=="baseline", pd0=pd; end
        fprintf('PDA %s ratioVsBand_r47_52=%.6f localFracRelRMSE=%.7f localBandRelRMSE=%.7f\n', ...
            prefix,r(1,2),norm(pd(local,2)-pd0(local,2))/norm(pd0(local,2)), ...
            norm(pd(local,3)-pd0(local,3))/norm(pd0(local,3)));
        if scenario~="baseline", continue, end
        aWide=carrier(t,y,75,150); emit(prefix,"AM75_150",diagnostics(t,aWide(:,3)));
        a40=carrier(t,y,35,45); emit(prefix,"AM35_45",diagnostics(t,a40(:,3)));
        a40Wide=carrier(t,y,33,48); emit(prefix,"AM33_48",diagnostics(t,a40Wide(:,3)));
        % Local long/short diagnostics can be independently inspected by age.
        writematrix([t,y,a100(:,3),a40(:,3),aWide(:,3),a40Wide(:,3)], ...
            fullfile('results',prefix+"_series.csv"));
        evalc('sp=spectralswafdr([t,y-mean(y)],''mtm'',2,5,0);');
        for pband={[35,45],[80,140]}
            bounds=pband{1};
            mask=sp(:,1)>=1/bounds(2) & sp(:,1)<=1/bounds(1) & islocalmax(sp(:,2));
            ids=find(mask); assert(~isempty(ids));
            [~,i]=max(sp(ids,2)./sp(ids,10)); k=ids(i);
            fprintf('CARRIER %s band=%d:%d bestPeriod=%.3f powerOverFDR=%.5f powerOverPointwise95=%.5f nLocalPeaksPassingBoth=%d\n', ...
                prefix,bounds,1/sp(k,1),sp(k,2)/sp(k,10),sp(k,2)/sp(k,5), ...
                sum(sp(ids,2)>sp(ids,5) & sp(ids,2)>sp(ids,10)));
        end
        phaseNull(t,a100(:,2),a100(:,3),prefix,"80_140");
        phaseNull(t,a40(:,2),a40(:,3),prefix,"35_45");
    end
end

function o = carrier(t,y,lo,hi)
    fl=1/hi; fh=1/lo;
    o=tanerhilbertML([t(:),y(:)-mean(y)],(fl+fh)/2,fl,fh,1e20);
end

function d = diagnostics(t,x)
    % Equal log-period spacing. |W|^2/scale removes the scale weighting of
    % the uncorrected Morlet spectrum. Keep only points outside edge effects.
    [w,per,sc,coi]=wavelet(x(:)',median(diff(t)),1,1/16,650,36,'Morlet',6);
    density=abs(w).^2./sc(:);
    old=t>=54000 & t<=60000;
    young=t>=44000 & t<=50000;
    local=t>=50000 & t<=53000;
    short=per>=1200 & per<=1600;
    long=per>=2000 & per<=2600;
    accepted=coi(:)>=max(per(short|long));
    old=old & accepted; young=young & accepted; local=local & accepted;
    d.oldShort=mean(density(short,old),'all'); d.oldLong=mean(density(long,old),'all');
    d.youngShort=mean(density(short,young),'all'); d.youngLong=mean(density(long,young),'all');
    d.localShort=mean(density(short,local),'all'); d.localLong=mean(density(long,local),'all');
    d.qOld=d.oldShort/d.oldLong; d.qYoung=d.youngShort/d.youngLong;
    % A separate ~1.2-Myr concentration score, equally weighting the two
    % flanking bands. Its phase-null preserves all stationary carrier lines.
    interior=t>=44000 & t<=60000 & accepted;
    core=per>=1050 & per<=1450;
    flank1=per>=700 & per<=950; flank2=per>=1600 & per<=2100;
    d.sScore=mean(density(core,interior),'all')/ ...
        ((mean(density(flank1,interior),'all')+mean(density(flank2,interior),'all'))/2);
end

function emit(label,which,d)
    fprintf('WAVE %s %s qOld=%.7f qYoung=%.7f contrast=%.7f shortLocal=%.8g longLocal=%.8g sScore=%.6f\n', ...
        label,which,d.qOld,d.qYoung,d.qOld/d.qYoung,d.localShort,d.localLong,d.sScore);
end

function phaseNull(t,filtered,observed,label,band)
    % Conditional on each carrier's observed global spectrum. Vectorized FFT
    % phase randomization preserves mean, Nyquist term and conjugate symmetry.
    observedStats=diagnostics(t,observed);
    x=fft(filtered(:)); n=numel(x); pos=(2:floor((n+1)/2))';
    B=199; contrast=zeros(B,1); concentration=zeros(B,1);
    for j=1:B
        z=x;
        z(pos)=abs(x(pos)).*exp(2i*pi*rand(size(pos)));
        z(n-pos+2)=conj(z(pos));
        proxy=abs(hilbert(real(ifft(z))));
        d=diagnostics(t,proxy);
        contrast(j)=log(d.qOld/d.qYoung); concentration(j)=d.sScore;
    end
    obs=log(observedStats.qOld/observedStats.qYoung);
    fprintf('PHASENULL %s %s B=%d pPositiveOldToYoung=%.4f pSconcentration=%.4f envelopeConsistency=%.3g\n', ...
        label,band,B,(1+sum(contrast>=obs))/(B+1), ...
        (1+sum(concentration>=observedStats.sScore))/(B+1), ...
        norm(abs(hilbert(filtered))-observed)/norm(observed));
    writematrix([contrast,concentration],fullfile('results',label+"_"+band+"_phase_null.csv"));
end

function orbitalChecks()
    t=(38000:5:67000)';
    path=fullfile('orbital-inputs','ems-plan3.dat');
    fid=fopen(path); for i=1:3, fgetl(fid); end
    c=textscan(fid,repmat('%f',1,8),'CommentStyle','#','CollectOutput',true); fclose(fid);
    b=c{1}; age=-b(:,1)/365250;
    z=interp1(age,[b(:,3),b(:,3).*sind(b(:,5)),sind(b(:,4)/2).*sind(b(:,6))],t);
    b=readmatrix(fullfile('orbital-inputs','La2010c.dat'),'FileType','text');
    l=interp1(-b(:,1),[hypot(b(:,4),b(:,5)),b(:,5),b(:,7)],t);
    b=readmatrix(fullfile('orbital-inputs','PT.dat'),'FileType','text');
    tilt=interp1(-b(:,1),b(:,2),t);
    assert(all(isfinite([z,l,tilt]),'all'));
    tilt40=carrier(t,tilt,35,45); emit("ZB18a","tiltAM35_45",diagnostics(t,tilt40(:,3)));
    spacing(t,tilt40(:,3),"ZB18a","tilt35_45");
    writematrix([t,tilt40(:,3)],fullfile('results','tilt_reference.csv'));
    for name=["ZB18a","La2010c"]
        if name=="ZB18a", data=z; else, data=l; end
        e=carrier(t,data(:,1),80,140); emit(name,"eccAM80_140",diagnostics(t,e(:,3)));
        h=carrier(t,data(:,2),70,75); p=carrier(t,data(:,3),68,74);
        emit(name,"h70_75",diagnostics(t,h(:,3))); emit(name,"p68_74",diagnostics(t,p(:,3)));
        spacing(t,h(:,3),name,"h70_75"); spacing(t,p(:,3),name,"p68_74");
        hWide=carrier(t,data(:,2),68,78); pWide=carrier(t,data(:,3),65,77);
        spacing(t,hWide(:,3),name,"h68_78"); spacing(t,pWide(:,3),name,"p65_77");
        % Resolve the two modes before differencing (eight-Myr Hann windows).
        modePair(t,data(:,2),name,"h",[68,78]); modePair(t,data(:,3),name,"p",[65,77]);
        writematrix([t,data,e(:,3),h(:,3),p(:,3)], ...
            fullfile('results',name+"_orbit_series.csv"));
    end
end

function spacing(t,a,label,band)
    % Fixed gentle 0.2 Myr running mean for beat times. Minimum separation
    % and prominence are held fixed across ages and across orbital solutions.
    b=movmean(a,round(200/median(diff(t))));
    use=t>=40000 & t<=65000;
    prom=0.10*(prctile(b(use),95)-prctile(b(use),5));
    [~,at]=findpeaks(b,t,'MinPeakDistance',650,'MinPeakProminence',prom);
    left=at(1:end-1); right=at(2:end); mid=(left+right)/2;
    delta=(right-left)/1000;
    for bounds={[40000,46000],[54000,60000]}
        v=bounds{1}; sel=mid>=v(1) & mid<=v(2);
        fprintf('SPACING %s %s midpointInterval=%d:%d n=%d medianMyr=%.5f allMyr=%s\n', ...
            label,band,v,sum(sel),median(delta(sel)),mat2str(delta(sel)',4));
    end
    writematrix([left,right,mid,delta],fullfile('results',label+"_"+band+"_beats.csv"));
end

function modePair(t,y,label,mode,band)
    for bounds={[39000,47000],[54000,62000]}
        v=bounds{1}; sel=t>=v(1) & t<v(2);
        u=detrend(y(sel)); dt=median(diff(t));
        [pow,f]=periodogram(u,hann(numel(u)),32768,1000/dt);
        in=f>=1000/band(2) & f<=1000/band(1);
        [heights,locs]=findpeaks(pow(in),f(in),'SortStr','descend','MinPeakDistance',0.22);
        assert(numel(locs)>=2); delta=abs(locs(1)-locs(2));
        fprintf('MODES %s %s interval=%d:%d f1=%.5f f2=%.5f cyclesPerMyr beatMyr=%.5f secondaryPowerFraction=%.5f\n', ...
            label,mode,v,locs(1),locs(2),1/delta,heights(2)/heights(1));
    end
end

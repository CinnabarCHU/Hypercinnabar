function modulation_timing()
    addpath(fullfile('upstream','code','seriesanalysis'));
    mkdir('timing');
    for site = ["1263","1209"]
        siteBackground(site);
    end
    for name = ["d13c","d18o"]
        a = readmatrix(fullfile('inputs',name+"_baseline_series.csv"));
        b = readmatrix(fullfile('inputs',name+"_baseline_pda.csv"));
        age = a(:,1);
        for sigma=[150,250]
            peakIntervals(age,a(:,3),name,"hilbert",sigma);
            peakIntervals(b(:,1),b(:,2),name,"PDAfraction",sigma);
            peakIntervals(b(:,1),b(:,3),name,"PDAband",sigma);
        end
        sampleSpectra(age,a(:,2),name);
    end
    for name = ["ZB18a","La2010c"]
        a = readmatrix(fullfile('inputs',name+"_orbit_series.csv"));
        for sigma=[150,250]
            peakIntervals(a(:,1),a(:,5),name,"eccHilbert",sigma);
            peakIntervals(a(:,1),a(:,6),name,"hHilbert",sigma);
        end
    end
end

function siteBackground(site)
    a=readmatrix(fullfile('inputs',site+".csv"));
    a=a(all(isfinite(a),2),:);
    [age,~,k]=unique(a(:,1));
    c=interpolate([age,accumarray(k,a(:,2),[],@mean)],5);
    o=interpolate([age,accumarray(k,a(:,3),[],@mean)],5);
    for width=[400,600,800]
        young=c(:,1)>=51000-width & c(:,1)<51000;
        old=c(:,1)>=51600 & c(:,1)<51600+width;
        selected=age>=51000-width & age<51600+width;
        fprintf('SITE %s windowKyr=%d diffYoungMinusOldC=%.5f O=%.5f nRawYoung=%d nRawOld=%d maxLocalGapKyr=%.3f\n', ...
            site,width,mean(c(young,2))-mean(c(old,2)),mean(o(young,2))-mean(o(old,2)), ...
            sum(a(:,1)>=51000-width & a(:,1)<51000),sum(a(:,1)>=51600 & a(:,1)<51600+width), ...
            max(diff(age(selected))));
    end
end

function peakIntervals(t,v,label,method,sigma)
    dt=median(diff(t)); half=ceil(4*sigma/dt);
    age=(-half:half)'*dt; weights=exp(-0.5*(age/sigma).^2);
    extended=[repmat(v(1),half,1);v;repmat(v(end),half,1)];
    smoothed=conv(extended,weights/sum(weights),'valid');
    inner=t>=41000 & t<=64000;
    span=prctile(smoothed(inner),95)-prctile(smoothed(inner),5);
    [~,at]=findpeaks(smoothed,t,'MinPeakDistance',650,'MinPeakProminence',0.10*span);
    left=at(1:end-1); right=at(2:end); mid=(left+right)/2;
    delta=(right-left)/1000;
    for bounds={[41000,47000],[47000,52000],[52000,55000]}
        w=bounds{1};sel=mid>=w(1) & mid<w(2); fully=left>=w(1) & right<=w(2);
        fprintf('TIMES %s %s sigma=%d ages=%d:%d n=%d median=%.4f allMyr=%s withinBoth=%s\n', ...
            label,method,sigma,w,sum(sel),median(delta(sel)), ...
            mat2str(delta(sel)',4),mat2str(delta(fully)',4));
    end
    writematrix([left,right,mid,delta],fullfile('timing',label+"_"+method+"_"+string(sigma)+".csv"));
end

function sampleSpectra(t,y,label)
    % Window spectra provide a small audit file against historical PDA
    % exports. FFT bins are the MATLAB array indices used in Acycle pdan.
    padded=zeropad2([t,y],800,1);
    n=fix(800/(padded(2,1)-padded(1,1)));
    selected=[1,410,825,1466,2346,3401,4001,4801,6001];
    ii=1; audit=zeros(2*7*numel(selected),2+2501);
    for offset=[0,1]
        for nw=[1.25,1.5,2,2.5,3,3.5,4]
            for ix=selected
                first=ix+offset;
                v=detrend(padded(first:first+n-1,2)');
                spec=pmtm(v,nw,5000);
                audit(ii,:)=[first,nw,spec(:)']; ii=ii+1;
            end
        end
    end
    writematrix(audit,fullfile('timing',label+"_pda_audit.csv"));
end

function runAcycleAlgorithmAudit(root)
% Compare pinned public code on the same observations. No upstream edits.
evidence = fullfile(root,'evidence');
scratch = tempname;
mkdir(scratch);
savedPath = path;
savedPwd = pwd;
cleanup = onCleanup(@() restoreSession(savedPath,savedPwd)); %#ok<NASGU>
cd(scratch);
set(groot,'defaultFigureVisible','off');
data = sortrows(readmatrix(fullfile(root,'benchmarks','fixtures','records','lavernock.csv')),1);
prepared = [data(:,1),data(:,2)-mean(data(:,2))];
rng(20261125,'twister');
noise = filter(1,[1,-0.65],randn(704,1));
noise = noise(193:end);
noise = noise-mean(noise);
report = struct;
for version = ["acycle","master"]
    path(savedPath);
    base = fullfile(root,'upstream',char(version),'code');
    addpath(fullfile(base,'seriesanalysis'),fullfile(base,'package','swa'),'-begin');
    clear specswafdr spectralswafdr specswa redconfML moveMedian rhoAR1 hpsort
    global unit2fid
    unit2fid = [];
    label = char(version);
    item = struct;
    try
        evalc('[f,p,b,~,~,fd]=specswafdr(data,0);');
        item.weedon = peakReport(f,p,b,fd(:,2));
        writematrix([f(:),p(:),b(:),fd(:,2)],fullfile(evidence,[label '-lomb.csv']));
    catch err
        item.weedon = struct('error',err.message);
    end
    for pad = [1 5]
        key = sprintf('mtm_pad%d',pad);
        try
            evalc('out=spectralswafdr(prepared,''mtm'',2,pad,0);');
            s = peakReport(out(:,1),out(:,2),out(:,3),out(:,10));
            s.direct_gamma_any = anyFdr(out(:,2)./out(:,3),6,2);
            assert(s.direct_gamma_any==s.any_fdr5,'FDR lookup and upper gamma disagree');
            item.(key) = s;
            writematrix(out,fullfile(evidence,sprintf('%s-mtm-pad%d.csv',label,pad)));
        catch err
            item.(key) = struct('error',err.message);
        end
    end
    for nw = [1 2]
        for fmax = [.25 .5]
            evalc('[r,s0,~,curve]=redconfML(noise,1,nw,512,2,.2,fmax,0);');
            key = sprintf('ml96_nw%d_f%d',nw,round(fmax*100));
            item.(key) = struct('rho',r,'s0',s0,'f_end',curve(end,1), ...
                'cl95_multiplier',curve(1,5)/curve(1,3),'rows',size(curve,1));
            writematrix(curve,fullfile(evidence,[label '-' key '.csv']));
        end
    end
    report.(label)=item;
    saveReport(evidence,report);
end

% The inexpensive decision below uses the production MTM and SWA estimates,
% replacing only the million-row chi-square lookup by the analytic upper tail.
% Bin-wise tests and the full denominator match the application. The same
% innovations drive all configurations. Synthetic noise has no periodic line.
trials = 240;
counts = zeros(2,2);
oracleCounts = zeros(2,2);
rng(3102026,'twister');
nullRhos = [.4 .8];
pads = [1 5];
for i=1:trials
    innovations = randn(704,1);
    for j=1:numel(nullRhos)
        r = nullRhos(j);
        y = filter(1,[1,-r],innovations);
        y = y(193:end);
        y = y-mean(y);
        for k=1:numel(pads)
            [power,w] = pmtm(y,2,512*pads(k));
            freq = w/(2*pi);
            b = specswa(freq,log10(power),length(y),false);
            counts(j,k) = counts(j,k)+anyFdr(power./b,6,2);
            % MATLAB's one-sided PSD is per radian/sample. DC and Nyquist
            % are not doubled. Innovation variance is one in this control.
            known = 1./(pi*(1-2*r*cos(w)+r^2));
            known([1 end]) = known([1 end])/2;
            oracleCounts(j,k) = oracleCounts(j,k)+anyFdr(power./known,6,2);
        end
    end
end
report.null_calibration = struct('trials',trials,'rhos',nullRhos,'pads',pads, ...
    'production_background_counts',counts,'known_background_counts',oracleCounts);
saveReport(evidence,report);

path(savedPath);
addpath(fullfile(root,'upstream','acycle','code','seriesanalysis'),'-begin');
addpath(fullfile(root,'upstream','recovered','code','package','timeOpt'),'-begin');
clear tanerhilbertML fitItls timeOptAc harm1ML
dat = readmatrix(fullfile(evidence,'odp926b-prepared-m.csv'));
dat(:,1) = dat(:,1)*100;
E = [405.6795,130.719,123.839,98.86307,94.87666];
P = [23.62069,22.31868,19.06768,18.91979];
evalc('[scan,~,~,~]=timeOptAc(dat,1.3,5,100,0,2,1,.035,.065,1000,E,P,1,1,0);');
R = readmatrix(fullfile(evidence,'odp926b-astrochron.csv'));
assert(size(scan,1)==size(R,1) && max(abs(scan(:,1)-R(:,1)))<1e-8);
writematrix(scan,fullfile(evidence,'odp926b-acycle.csv'));
[mp,ip]=max(scan(:,4));
[mr,ir]=max(R(:,4));
report.timeopt = struct('acycle_rate',scan(ip,1),'acycle_r2',mp, ...
    'astrochron_rate',R(ir,1),'astrochron_r2',mr, ...
    'max_abs_curve_difference',max(abs(scan(:,2:4)-R(:,2:4)),[],1));
% Isolate fitting from filtering. A near-cancelling pair of close targets
% lies exactly in the joint harmonic subspace.
t = (0:399)';
periods = [94.87666 98.86307];
X = [cos(2*pi*t/periods(1)) sin(2*pi*t/periods(1)) ...
     cos(2*pi*t/periods(2)) sin(2*pi*t/periods(2))];
y = X(:,1)-X(:,3);
joint = [ones(size(t)),X];
jointFit = joint*(joint\y);
[separate,~] = fitItls([t y],1,periods,1,1,0);
[nominalSpearman,~] = fitItls([t y],1,periods,2,1,0);
report.harmonic_control = struct('joint_r2',corr(y,jointFit)^2, ...
    'acycle_r2',separate,'acycle_spearman_option',nominalSpearman);
saveReport(evidence,report);
report.other_nulls = compareLegacyAndNative(root,savedPath);
saveReport(evidence,report);
for version = ["acycle","master"]
    path(savedPath);
    base=fullfile(root,'upstream',char(version),'code');
    addpath(fullfile(base,'seriesanalysis'),fullfile(base,'package','swa'),'-begin');
    clear specswa spectralswafdr
    t=(0:511)';
    positive=[t,noise+4*sin(2*pi*t/32)];
    evalc('o=spectralswafdr(positive,''mtm'',2,1,0);');
    tableResult=any(isfinite(o(:,10)));
    gammaResult=anyFdr(o(:,2)./o(:,3),6,2);
    assert(tableResult && gammaResult,'Injected line did not pass both FDR implementations');
    report.(char(version)).signal_control=struct('lookup',tableResult,'analytic',gammaResult);
end
saveReport(evidence,report);
end

function result = compareLegacyAndNative(root,savedPath)
path(savedPath);
base = fullfile(root,'upstream','acycle','code');
addpath(fullfile(base,'seriesanalysis'),fullfile(base,'package','swa'),'-begin');
clear specswa specswafdr spectralswafdr
global unit2fid
unit2fid = [];
trials=240;
nativeTrials=80;
rhos=[.4 .8];
pads=[1 5];
hits=zeros(2,2);
failures=zeros(2,2);
nativeHits=zeros(1,2);
nativeFailures=zeros(1,2);
messages={};
rng(3102026,'twister');
for i=1:trials
    innovations=randn(704,1);
    for j=1:numel(rhos)
        y=filter(1,[1,-rhos(j)],innovations);
        y=y(193:end);
        y=y-mean(y);
        data=[(0:length(y)-1)',y];
        if i<=nativeTrials
            try
                evalc('[~,~,~,~,~,fd]=specswafdr(data,0);');
                nativeHits(j)=nativeHits(j)+any(isfinite(fd(:,2)));
            catch err
                nativeFailures(j)=nativeFailures(j)+1;
                messages=unique([messages,{err.message}]);
            end
        end
        for k=1:numel(pads)
            try
                [power,w]=pmtm(y,2,512*pads(k));
                freq=w/(2*pi);
                evalc('b=specswa(freq,log10(power),length(y));');
                hits(j,k)=hits(j,k)+anyFdr(power./b,6,2);
            catch err
                failures(j,k)=failures(j,k)+1;
                messages=unique([messages,{err.message}]);
            end
        end
    end
end
result=struct('trials',trials,'rhos',rhos,'pads',pads,'legacy_hits',hits, ...
    'legacy_errors',failures,'native_trials',nativeTrials,'native_hits',nativeHits, ...
    'native_errors',nativeFailures,'error_messages',{messages});
end

function s = peakReport(f,p,b,level)
f = f(:); p = p(:); b = b(:); level = level(:);
peak = false(size(p));
peak(2:end-1) = p(2:end-1)>p(1:end-2) & p(2:end-1)>=p(3:end);
eligible=find(peak & f>=1/.88 & f<=1/.74);
assert(~isempty(eligible),'No local peak in the declared Lavernock interval');
[~,i]=max(p(eligible)); bin=eligible(i);
s=struct('bins',numel(f),'peak_wavelength',1/f(bin),'power',p(bin), ...
    'background',b(bin),'ratio',p(bin)/b(bin),'fdr5_threshold',level(bin), ...
    'any_fdr5',any(isfinite(level)),'peak_above_fdr5',p(bin)>level(bin));
end

function yes=anyFdr(ratio,nu,nw)
p = sort(gammainc(ratio(:)*nu/2,nu/2,'upper'));
n = numel(p);
yes = any(p<(.05*(1:n)'/(n*sum(1./(1:nw)))));
end

function saveReport(folder,report)
fid=fopen(fullfile(folder,'summary.json'),'w');
guard=onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s\n',jsonencode(report,'PrettyPrint',true));
end

function restoreSession(previousPath,previousPwd)
path(previousPath);
cd(previousPwd);
end

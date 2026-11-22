function [retval, id] = analyzer(params, id)
% CircularSpectrum.analyzer parameters: data p1 p2 pn linlog clmodel mcn smoothwin(red).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/circularspecGUI.m#L228
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('CircularSpectrum-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
p1 = p.p1;
p2 = p.p2;
pn = p.pn;
linlog = p.linlog;
clmodel = p.clmodel;
mcn = p.mcn;
handles.linLog=linlog;
if ~ismember(clmodel,1:3), error('Acycle:CSA:NoiseModel','Unknown confidence model.'); end
if clmodel == 3
    smoothwin=p.smoothwin;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/circularspecGUI.m:L260-L261
            nw = 2; % number
            rho = 0.5; % prior
%% End copied source
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/circularspecGUI.m:L274-L373
RR = zeros(mcn,pn);
plotn = 0;  % no plot for the Monte Carlo simulations
if clmodel < 3
    % Monte Carlo
    if clmodel == 1
        for i = 1:mcn
            t2 = diff(data);
            tn3 = randperm(length(t2));
            tn4= [0;cumsum(t2(tn3))];
            [~,Ri,~] = circularspec(tn4,p1,p2,pn,handles.linLog,plotn);
            RR(i,:) = Ri;
        end
    elseif clmodel == 2
        a = rand(length(data),mcn)*(max(data)-min(data)) + min(data);
        for i = 1:mcn    
            [~,Ri,~] = circularspec(a(:,i),p1,p2,pn,handles.linLog,plotn);
            RR(i,:) = Ri;
        end
    end

    % percentile
    prt = [50,90,95,99];
    Y = prctile(RR,prt,1);

    % real power spectrum
    [P,R,t0] = circularspec(data,p1,p2,pn,handles.linLog,0);

    % confidence levels using Monte Carlo
    cl = zeros(1,pn);
    for j = 1: length(cl)
        percj = [RR(:,j);R(j)];
        cl(j) = length(percj(percj<R(j)))/(1+mcn);
    end

    if clmodel == 2
        % theory white noise
        theowhite = ones(1,pn)*mean(Y(1,:));
        nw = 2;
        K = 2*nw -1;
        nw2 = 2*(K);
        chi90 = theowhite * chi2inv(0.90,nw2)/nw2;
        chi95 = theowhite * chi2inv(0.95,nw2)/nw2;
        chi99 = theowhite * chi2inv(0.99,nw2)/nw2;
        chi999 = theowhite * chi2inv(0.999,nw2)/nw2;

        chi2norm = R./theowhite';
        chi2normnw2 = chi2norm' * nw2;
        pll = chi2cdf(chi2normnw2,nw2);
        
        Y1 = [theowhite',chi90',chi95',chi99',chi999'];
    end
    
elseif clmodel == 3
    % red noise
    %number of data points
    datan = length(data);
    datan1 = datan -1;

    % test Period
    if linlog == 2
        P = linspace(p1,p2,pn);
    else
        sedinc = (log10(p2) - log10(p1))/(pn-1);
        P = zeros(1,pn);
        for ii = 1: pn
            P(ii) = 10^(  log10(p1)  +  (ii-1) * sedinc ) ;
        end
    end

    % real power spectrum
    [P,R,t0] = circularspec(data(:,1),p1,p2,pn,linlog,0);

    s0 = mean(R);
    duration = max(data(:,1)) - min(data(:,1));
    fmax = 1/(2 * duration/datan);

    ft = 1./P;
    ft = ft';
    pxxsmooth = moveMedian(R,round(smoothwin*length(R)));

    cospara = cos(pi.*ft./fmax);
    funrobust = @(v,f)v(1) * (1-v(2)^2)./(1-(2.*v(2).*cospara)+v(2)^2);
    v1 = [s0,rho];
    x = lsqcurvefit(funrobust,v1,ft,pxxsmooth);
    rhoM = x(2);
    s0M = x(1);
    disp('>>    MTM rho and S0 estimation: curve fitting method')

    % median-smoothing reshape significance level
    theored1 = s0M * (1-rhoM^2)./(1-(2.*rhoM.*cos(pi.*ft./fmax))+rhoM^2);

    K = 2*nw -1;
    nw2 = 2*(K);
    % Chi-square inversed distribution
    chi90 = theored1 * chi2inv(0.90,nw2)/nw2;
    chi95 = theored1 * chi2inv(0.95,nw2)/nw2;
    chi99 = theored1 * chi2inv(0.99,nw2)/nw2;
    chi999 = theored1 * chi2inv(0.999,nw2)/nw2;
    
end
%% End copied source
r = struct();
r.P = P;
r.R = R;
r.t0 = t0;
r.pn = pn;
r.p1 = p1;
r.p2 = p2;
r.clmodel = clmodel;
if clmodel < 3, r.Y=Y; r.cl=cl; end
if clmodel==2, r.theowhite=theowhite; r.pll=pll; end
if clmodel>=2, r.chi90=chi90; r.chi95=chi95; r.chi99=chi99; r.chi999=chi999; end
if clmodel==3, r.theored1=theored1; r.pxxsmooth=pxxsmooth; r.smoothwin=smoothwin; r.nw2=nw2; end
end

function [retval, id] = analyzer(params, id)
% SpectralBendingPowerLaw.analyzer parameters: datax fd1 po method nw(MTM).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L687
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L1722
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SpectralBendingPowerLaw-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
datax = p.datax;
fd1 = p.fd1;
po = p.po;
method = p.method;
switch method
case 'Multi-taper method'
    nw=p.nw;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L687-L711
        N = length(datax);
        % With no padding or smoothing applied
        % Number of independent Fourier frequencies
        Nf = N/2;
        pol = log(po);
        pol = real(pol);
        fun = @(v,f)(v(1) * f .^(-1 * v(2)))./(1 + (f / v(4)) .^ (v(3)-v(2)));
        v0 = [100,0.5,3,0.5*fd1(end)];
        x = lsqcurvefit(fun,v0,fd1(2:end),pol(2:end));
        theored1 = exp(fun(x,fd1)); % bending power law fit
        K = 2*nw -1;
        nw2 = 2*(K);
        % Chi-square inversed distribution
        % local c.l.
        red90 = theored1 * chi2inv(0.90,nw2)/nw2;
        red95 = theored1 * chi2inv(0.95,nw2)/nw2;
        red99 = theored1 * chi2inv(0.99,nw2)/nw2;
        
        % periodogram method global
        alpha90 = 0.10/Nf;
        alpha95 = 0.05/Nf;
        alpha99 = 0.01/Nf;
        red90global = theored1 * chi2inv((1-alpha90),nw2)/nw2;
        red95global = theored1 * chi2inv((1-alpha95),nw2)/nw2;
        red99global = theored1 * chi2inv((1-alpha99),nw2)/nw2;
%% End copied source
pl=theored1;
case {'Lomb-Scargle spectrum','Periodogram'}
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1722-L1744
        N = length(datax);
        % With no padding or smoothing applied
        % Number of independent Fourier frequencies
        Nf = N/2;
        
        pol = log(po);
        pol = real(pol);
        
        fun = @(v,f)(v(1) * f .^(-1 * v(2)))./(1 + (f / v(4)) .^ (v(3)-v(2)));
        v0 = [100,0.5,3,0.5*fd1(end)];
        x = lsqcurvefit(fun,v0,fd1(2:end),pol(2:end));
        pl = exp(fun(x,fd1));
        % local c.l.
        red90 = pl * chi2inv(0.9,2)/2;
        red95 = pl * chi2inv(0.95,2)/2;
        red99 = pl * chi2inv(0.99,2)/2;
        % periodogram method global
        alpha90 = 0.1/Nf;
        alpha95 = 0.05/Nf;
        alpha99 = 0.01/Nf;
        red90global = pl * chi2inv((1-alpha90),2)/2;
        red95global = pl * chi2inv((1-alpha95),2)/2;
        red99global = pl * chi2inv((1-alpha99),2)/2;
%% End copied source
otherwise, error('Acycle:Spectrum:Method','Unknown estimator.'); end
r = struct();
r.fd1 = fd1;
r.po = po;
r.pl = pl;
r.red90 = red90;
r.red95 = red95;
r.red99 = red99;
r.red90global = red90global;
r.red95global = red95global;
r.red99global = red99global;
end

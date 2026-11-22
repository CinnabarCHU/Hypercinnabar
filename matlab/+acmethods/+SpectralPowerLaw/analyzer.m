function [retval, id] = analyzer(params, id)
% SpectralPowerLaw.analyzer parameters: datax fd1 po method nw(MTM).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L577
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L1615
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SpectralPowerLaw-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
datax = p.datax;
fd1 = p.fd1;
po = p.po;
method = p.method;
switch method
case 'Multi-taper method'
    nw=p.nw;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L577-L601
        K = 2*nw -1;
        nw2 = 2*(K);
        
        N = length(datax);
        % With no padding or smoothing applied
        % Number of independent Fourier frequencies
        Nf = N/2; 
        pf = polyfit(log(fd1(2:end)),log(po(2:end)),1);
        % Evaluating Coefficients
        a = pf(1);
        % Accounting for the log transformation
        k = exp(pf(2));
        %ezplot(@(X) k*X.^a,[X(1) X(end)])
        pl = k * fd1.^a;
        % local c.l.
        red90 = pl * chi2inv(0.9,nw2)/nw2;
        red95 = pl * chi2inv(0.95,nw2)/nw2;
        red99 = pl * chi2inv(0.99,nw2)/nw2;
        % periodogram method global
        alpha90 = 0.1/Nf;
        alpha95 = 0.05/Nf;
        alpha99 = 0.01/Nf;
        red90global = pl * chi2inv((1-alpha90),nw2)/nw2;
        red95global = pl * chi2inv((1-alpha95),nw2)/nw2;
        red99global = pl * chi2inv((1-alpha99),nw2)/nw2;
%% End copied source
case {'Lomb-Scargle spectrum','Periodogram'}
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1615-L1636
        N = length(datax);
        % With no padding or smoothing applied
        % Number of independent Fourier frequencies
        Nf = N/2; 
        pf = polyfit(log(fd1(2:end)),log(po(2:end)),1);
        % Evaluating Coefficients
        a = pf(1);
        % Accounting for the log transformation
        k = exp(pf(2));
        %ezplot(@(X) k*X.^a,[X(1) X(end)])
        pl = k * fd1.^a;
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

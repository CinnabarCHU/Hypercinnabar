function [retval,id] = analyzer(params,id)
% PowerSpectrum.analyzer parameters: data method nw nfft fmin fmax models; robust uses fitModel smoothFraction fitMaximum.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PowerSpectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function [r,status] = execute(p)
data=p.data; method=validatestring(p.method,{'Multi-taper method','Periodogram','Lomb-Scargle spectrum'});
if size(data,2)<2 || size(data,1)<8, error('Acycle:Spectrum:Rows','At least eight two-column samples are required.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L397-L399
                x = data(:,1);
                y = data(:,2) - mean(data(:,2),'omitnan');
                dt = median(diff(x));
%% End copied source
if ~isfinite(dt) || dt<=0, error('Acycle:Spectrum:Spacing','Invalid median spacing.'); end
nw=p.nw; nfft=p.nfft; fmin=p.fmin; fmax=p.fmax; app.nyquist=1/(2*dt);
if ~(isscalar(nfft) && isfinite(nfft) && nfft>=1 && nfft==fix(nfft)), error('Acycle:Spectrum:NFFT','Expected an exact positive integer.'); end
if ~(isscalar(fmin) && isfinite(fmin) && fmin>=0 && isscalar(fmax) && isfinite(fmax) && fmax>fmin)
    error('Acycle:Spectrum:FrequencyRange','Supply a finite increasing nonnegative display interval.');
end
if contains(lower(method),'multi') && ~(isscalar(nw) && nw<numel(y)/2 && (nw==1 || nw>=1.25))
    error('Acycle:Spectrum:Bandwidth','Invalid MTM time-bandwidth product.');
end
active={'robust','classic','ftest','swa','powerLaw','bendingPowerLaw'};
accompat.requireFields(p.models,active);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L499-L511
                calculationMaximum = app.nyquist;
                if contains(lower(method),'lomb')
                    % Unevenly sampled Lomb spectra do not have a strict
                    % Nyquist cutoff.  v2.8 honored an explicitly larger
                    % FMAX; retain the physical Nyquist as the minimum
                    % calculation range so lower display limits do not
                    % change full-spectrum fits or saved output.
                    calculationMaximum = max(app.nyquist,fmax);
                end
                [fFull,pFull] = computeSpectrum( ...
                    method,y,x,dt,nw,nfft,calculationMaximum);
                keep = isfinite(fFull) & isfinite(pFull) & ...
                    (fFull >= fmin) & (fFull <= fmax);
%% End copied source
r=struct('frequency',fFull,'power',pFull,'displayMask',keep,'dof',spectrumConfidenceDegreesOfFreedom(method,nw), ...
    'physicalNyquist',app.nyquist,'nfft',nfft,'models',struct(),'issues',struct());
r.method=method; r.nw=nw; r.fmin=fmin; r.fmax=fmax;
if p.models.robust, r.smoothFraction=p.smoothFraction; end
status='done';
for k=1:numel(active)
    name=active{k};
    if ~p.models.(name), continue; end
    try
        r.models.(name)=background(name,method,x,y,dt,nw,nfft,fmin,fmax,app.nyquist,calculationMaximum,fFull,pFull,p);
    catch err
        r.issues.(name)=struct('identifier',err.identifier,'message',err.message);
        fprintf('%s: %s\n',name,err.message);
        status='incomplete';
    end
end
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1569-L1584
        function [f,p] = computeSpectrum(method,y,x,dt,nw,nfft,physicalNyquist)
            if contains(lower(method),'multi')
                if nw == 1
                    [p,w] = pmtm(y,nw,nfft,'DropLastTaper',false);
                else
                    [p,w] = pmtm(y,nw,nfft);
                end
                f = w/(2*pi*dt);
            elseif contains(lower(method),'periodogram')
                [p,f] = periodogram(y,[],nfft,1/dt);
            else
                [p,f] = plomb(y,x+abs(min(x)),physicalNyquist);
            end
            f = real(f(:));
            p = real(p(:));
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1608-L1615
        function dof = spectrumConfidenceDegreesOfFreedom(method,nw)
            % Do not evaluate an inactive MTM setting for periodogram/Lomb.
            if contains(lower(method),'multi')
                dof = 2*acycleMtmTaperCount(nw);
            else
                dof = 2;
            end
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1586-L1606
        function [pl,loc90,loc95,loc99,g90,g95,g99] = ...
                powerLawLevels(f,p,dof,Nf)
            ff = f(:); pp = p(:);
            good = ff > 0 & isfinite(ff) & isfinite(pp) & pp > 0;
            ff = ff(good); pp = pp(good);
            if numel(ff) < 2
                error('spectrum:insufficientPowerLawData', ...
                    'At least two positive finite spectral ordinates are required.');
            end
            pf = polyfit(log(ff),log(pp),1);
            a = pf(1); k = exp(pf(2));
            pl = NaN(size(f));
            evalGood = f > 0 & isfinite(f);
            pl(evalGood) = k * f(evalGood).^a;
            loc90 = pl * chi2inv(0.90,dof)/dof;
            loc95 = pl * chi2inv(0.95,dof)/dof;
            loc99 = pl * chi2inv(0.99,dof)/dof;
            g90 = pl * chi2inv(1-0.10/Nf,dof)/dof;
            g95 = pl * chi2inv(1-0.05/Nf,dof)/dof;
            g99 = pl * chi2inv(1-0.01/Nf,dof)/dof;
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1617-L1662
        function [bpl,loc90,loc95,loc99,g90,g95,g99] = ...
                bendingPowerLawLevels(f,p,dof,Nf)
            ff = f(:); pp = p(:);
            good = ff > 0 & isfinite(ff) & isfinite(pp) & pp > 0;
            ff = ff(good); pp = pp(good);
            if numel(ff) < 4
                error('spectrum:insufficientBendingPowerLawData', ...
                    'At least four positive finite spectral ordinates are required.');
            end
            % Fit the BPL in log-power space. The legacy expression fitted a
            % linear-power model directly to LOG(P) and then exponentiated
            % it, which is not a bending power law and permits invalid bend
            % frequencies. Parameter 3 is a log positive slope increment,
            % scaled by the fitted log-frequency range for conditioning.
            logFrequencyRange = log(ff(end))-log(ff(1));
            if ~(isfinite(logFrequencyRange) && logFrequencyRange > 0)
                error('spectrum:insufficientBendingPowerLawRange', ...
                    'Bending-power-law fitting requires distinct frequencies.');
            end
            logModel = @(v,fx) v(1)-v(2).*log(fx)-stableSoftplus( ...
                (exp(v(3))/logFrequencyRange).* ...
                (log(fx)-v(4)));
            initialSlopeIncrement = 2.5;
            v0 = [log(median(pp)),0.5, ...
                log(initialSlopeIncrement*logFrequencyRange), ...
                0.5*(log(ff(1))+log(ff(end)))];
            lowerBounds = [-Inf,0,log(eps),log(ff(1))];
            upperBounds = [Inf,20,log(40*logFrequencyRange),log(ff(end))];
            options = optimoptions('lsqcurvefit','Display','off');
            v = lsqcurvefit(logModel,v0,ff,log(pp), ...
                lowerBounds,upperBounds,options);
            bpl = NaN(size(f));
            evalGood = f > 0 & isfinite(f);
            bpl(evalGood) = exp(logModel(v,f(evalGood)));
            bpl = bpl(:);
            loc90 = bpl * chi2inv(0.90,dof)/dof;
            loc95 = bpl * chi2inv(0.95,dof)/dof;
            loc99 = bpl * chi2inv(0.99,dof)/dof;
            g90 = bpl * chi2inv(1-0.10/Nf,dof)/dof;
            g95 = bpl * chi2inv(1-0.05/Nf,dof)/dof;
            g99 = bpl * chi2inv(1-0.01/Nf,dof)/dof;
        end

        function value = stableSoftplus(value)
            value = max(value,0)+log1p(exp(-abs(value)));
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1016-L1036
        function outputdata = runSpectralSwa(dataForSwa,nw,padtimes)
            oldDir = pwd;
            cleanupDir = tempname;
            mkdir(cleanupDir);
            cleanup = onCleanup(@()restoreAfterSwa(oldDir,cleanupDir));
            cd(cleanupDir);
            outputdata = spectralswafdr(dataForSwa,'mtm',nw,padtimes,0);
        end

        function restoreAfterSwa(oldDir,cleanupDir)
            try
                cd(oldDir);
            catch
            end
            if ~isempty(cleanupDir) && isfolder(cleanupDir)
                try
                    rmdir(cleanupDir,'s');
                catch
                end
            end
        end
%% End copied source

function value = background(which,method,x,y,dt,nw,nfft,fmin,fmax,physical,calculationMaximum,fFull,pFull,p)
app.nyquist = physical;
dof = spectrumConfidenceDegreesOfFreedom(method,nw);
switch which
case 'robust'
    robustFitModel = p.fitModel; robustSmoothingFraction = p.smoothFraction; robustFitMaximum=p.fitMaximum;
    if contains(lower(method),'multi')
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L557-L561
                        [rhoM,s0M,redconfAR1,redconfML96] = redconfML( ...
                            y,dt,nw,nfft,robustFitModel, ...
                            robustSmoothingFraction, ...
                            min(fmax,app.nyquist),0, ...
                            robustFitMaximum); %#ok<ASGLU>
%% End copied source
        value=struct('rho',rhoM,'s0',s0M,'smoothed',redconfAR1,'levels',redconfML96);
    elseif contains(lower(method),'lomb')
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L580-L582
                        [pR,fR,pth] = plomb_robustar1( ...
                            y,x+abs(min(x)),fmax,robustSmoothingFraction,0);
                        rr = fR >= fmin & fR <= fmax;
%% End copied source
        value=struct('frequency',fR,'power',pR,'levels',pth,'displayMask',rr);
    else, error('Acycle:Spectrum:InactiveModel','Robust AR(1) requires MTM or Lomb.'); end
case 'classic'
    if contains(lower(method),'multi')
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L600-L601
                            [fc,pClassic,theo,c90,c95,c99,c999] = ...
                                redconfchi2(y,nw,dt,nfft,2);
%% End copied source
    elseif contains(lower(method),'periodogram')
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L617-L618
                            [fc,pClassic,theo,c90,c95,c99,c999] = ...
                                redconfchi2(y,1,dt,nfft,1);
%% End copied source
    else
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L634-L638
                            pfa = [0.50 0.10 0.01 0.0001];
                            pd = 1 - pfa;
                            [pLS,fLS,pth] = plomb( ...
                                y,x+abs(min(x)),calculationMaximum, ...
                                'Pd',pd);
%% End copied source
        value=struct('frequency',fLS,'power',pLS,'levels',pth); return
    end
    value=[fc(:),pClassic(:),theo(:),c90(:),c95(:),c99(:),c999(:)];
case 'ftest'
    if ~contains(lower(method),'multi'), error('Acycle:Spectrum:InactiveModel','The F-test requires MTM.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L690-L692
                        padtimes = nfft/numel(y);
                        [freq,ftest,fsig,Amp,Faz,Sig,Noi,dof,~] = ...
                            ftestmtmML([x y],nw,padtimes,0);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L693-L701
                        freq = freq(:); ftest = ftest(:); fsig = fsig(:);
                        Amp = Amp(:); Faz = Faz(:); Sig = Sig(:);
                        Noi = Noi(:); dof = dof(:);
                        oneSided = isfinite(freq) & freq >= 0 & ...
                            freq <= app.nyquist;
                        freq = freq(oneSided); ftest = ftest(oneSided);
                        fsig = fsig(oneSided); Amp = Amp(oneSided);
                        Faz = Faz(oneSided); Sig = Sig(oneSided);
                        Noi = Noi(oneSided); dof = dof(oneSided);
%% End copied source
    value=struct('frequency',freq,'F',ftest,'significance',fsig,'amplitude',Amp,'phase',Faz,'signal',Sig,'noise',Noi,'dof',dof);
case 'swa'
    if ~contains(lower(method),'multi'), error('Acycle:Spectrum:InactiveModel','SWA requires MTM.'); end
    value=runSpectralSwa([x,y],nw,nfft/numel(y));
case {'powerLaw','bendingPowerLaw'}
    if strcmp(which,'powerLaw'), fit=@powerLawLevels; else, fit=@bendingPowerLawLevels; end
    [level,a,b,c,g,h,i]=fit(fFull,pFull,dof,numel(y)/2);
    value=[fFull(:),level(:),a(:),b(:),c(:),g(:),h(:),i(:)];
end
end

function acMenuValidate(engine,p)
% Validate this role's scientific selectors before entering its numerical implementation.
if ~ismember('analyzer',strsplit(engine.roles))
    error('Acycle:Menu:Role','%s has no analyzer in the selected snapshot.',engine.operation);
end
if ~isempty(engine.required), acMenuRequire(p,strsplit(engine.required)); end
legacy=strcmp(engine.revision,'guide');
switch engine.package
case 'PowerSpectrum'
    if legacy
        acMenuRequire(p.noise,{'classic','robust','ftest','swa','powerlaw','bending','smoothwin','linlog','biascorr'});
        if strcmp(p.method,'Lomb-Scargle spectrum'), acMenuRequire(p,{'pd'}); else, acMenuRequire(p,{'padtimes'}); end
        if p.noise.robust && strcmp(p.method,'Multi-taper method')
            if p.noise.biascorr, acMenuRequire(p,{'ValidNyqFreqR'}); else, acMenuRequire(p,{'ValidNyqFreq'}); end
        end
    else
        flags={'classic','robust','ftest','swa','powerLaw','bendingPowerLaw'};
        acMenuRequire(p.models,flags);
        for n=flags
            flag=p.models.(n{1});
            if ~(islogical(flag) || isnumeric(flag)) || ~isscalar(flag) || ~ismember(flag,[0 1])
                error('Acycle:Menu:Option','Invalid models.%s.',n{1});
            end
        end
        if p.models.robust
            acMenuRequire(p,{'fitModel','fitMaximum','smoothFraction'});
            for n={'fitModel','fitMaximum','smoothFraction'}
                if isempty(p.(n{1})), error('Acycle:Menu:MissingOption','Empty active %s.',n{1}); end
            end
        end
    end
case 'Detrending'
    if strcmp(p.method,'polynomial'), acMenuRequire(p,{'degree'}); end
    if ismember(p.method,{'lowess','rlowess','loess','rloess'}), acMenuRequire(p,{'span'}); end
case 'DataTransform'
    if p.j==2, acMenuRequire(p,{'edit1','edit2'}); end
    if p.j==7, acMenuRequire(p,{'edit3'}); end
    if p.j==10, acMenuRequire(p,{'edit4'}); end
case 'Bandpass'
    if legacy
        if strcmp(p.filter,'Taner-Hilbert'), acMenuRequire(p,{'taner_c'}); end
    else
        acMenuRequire(p.options,{'method','lower_frequency','upper_frequency'});
        if strcmpi(p.options.method,'taner_hilbert'), acMenuRequire(p.options,{'rolloff_exponent'}); end
    end
case 'PassFilter'
    if strcmp(p.passtype,'bandstopiir'), acMenuRequire(p,{'f12'}); end
case 'CircularSpectrum'
    if legacy && p.clmodel==3, acMenuRequire(p,{'smoothwin'}); end
case {'SpectralPowerLaw','SpectralBendingPowerLaw'}
    if legacy && strcmp(p.method,'Multi-taper method'), acMenuRequire(p,{'nw'}); end
case 'AstronomicalSolution'
    if strcmp(p.parameter,'ETP')
        if legacy, acMenuRequire(p,{'wE','wT','wP'}); else, acMenuRequire(p,{'weights'}); end
    end
case 'TimeOpt'
    if p.nsim>1, acMenuRequire(p,{'mc_scope'}); end
case 'Lyapunov'
    if ~isfield(p,'data_even'), acMenuRequire(p,{'data','interpolate_rate','padtype'}); end
case 'SeriesGenerator'
    switch p.kind
    case 'polynomial'
        acMenuRequire(p,{'intercept','coefficients'});
    case {'harmonic','sinusoid'}
        acMenuRequire(p,{'amplitude','period','phase','offset'});
        if p.period==0, error('Acycle:Menu:Option','The period must be nonzero.'); end
    case {'white','red','gaussian','uniform'}
        if legacy, acMenuRequire(p,{'mean','std'}); else, acMenuRequire(p,{'mu','sigma'}); end
        if strcmp(p.kind,'white'), acMenuRequire(p,{'distribution'}); end
        if strcmp(p.kind,'red'), acMenuRequire(p,{'alpha'}); end
    end
case 'Recurrence'
    if isempty(p.threshold) || isempty(p.normFlag) || isempty(p.method_use)
        error('Acycle:Menu:MissingOption','Explicit recurrence method, normalization and threshold are required.');
    end
end
end

function acMenuRequire(s,names)
for k=1:numel(names)
    parts=strsplit(names{k},'.');
    value=s;
    for j=1:numel(parts)
        if ~isstruct(value) || ~isscalar(value) || ~isfield(value,parts{j})
            error('Acycle:Menu:MissingOption','Required option %s is missing.',names{k});
        end
        value=value.(parts{j});
    end
end
end

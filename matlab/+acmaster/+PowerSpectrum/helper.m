function [retval,id] = helper(params,id)
% PowerSpectrum.helper parameters: data; optional method and models.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PowerSpectrum-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
app.data=sortrows(p.data);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L27-L37
        app.method = "Multi-taper method";
        app.activeMethod = "";
        app.nyquist = estimateNyquist(app.data);
        app.isUneven = acycleSamplingIsUneven(app.data(:,1));
        app.mtmNoiseState = struct('Robust',true,'Classic',false, ...
            'Ftest',false,'Swa',~app.isUneven);
        app.periodogramNoiseState = struct('Classic',false);
        app.lombNoiseState = struct('Robust',true,'Classic',false);
        [app.biasCorrectionRecommended,app.biasCorrectionFitMaximum] = ...
            recommendUltraHighResolutionBiasCorrection( ...
            app.data,app.nyquist,~app.isUneven);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L47-L51
        defaultMethod = 'Multi-taper method';
        if app.isUneven
            defaultMethod = 'Lomb-Scargle spectrum';
            app.method = "Lomb-Scargle spectrum";
        end
%% End copied source
if isfield(p,'method'), defaultMethod = validatestring(p.method, ...
    {'Multi-taper method','Periodogram','Lomb-Scargle spectrum'}); end
models = struct('robust',false,'classic',false,'ftest',false,'swa',false,'powerLaw',false,'bendingPowerLaw',false);
switch defaultMethod
    case 'Multi-taper method'
        models.robust = app.mtmNoiseState.Robust; models.swa = app.mtmNoiseState.Swa;
    case 'Lomb-Scargle spectrum'
        models.robust = app.lombNoiseState.Robust;
end
if isfield(p,'models'), models = accompat.overrideOptions(models,p.models); end
fitMaximum = app.nyquist;
if app.biasCorrectionRecommended, fitMaximum = app.biasCorrectionFitMaximum; end
r=struct('data',app.data,'method',defaultMethod,'nw',2,'nfft',size(app.data,1), ...
    'fmin',0,'fmax',fitMaximum,'models',models,'fitModel',1, ...
    'physicalNyquist',app.nyquist,'recommendedBiasCorrection',app.biasCorrectionRecommended, ...
    'fitMaximum',fitMaximum,'smoothFraction',0.2, ...
    'mtmNoise',app.mtmNoiseState,'lombNoise',app.lombNoiseState,'periodogramNoise',app.periodogramNoiseState);
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1906-L1917
function n = estimateNyquist(data)
if size(data,1) < 3
    n = 0.5;
    return;
end
dt = median(diff(data(:,1)));
if ~(isfinite(dt) && dt > 0)
    n = 0.5;
else
    n = 1/(2*dt);
end
end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1919-L1956
function [recommended,fitMaximum] = ...
        recommendUltraHighResolutionBiasCorrection( ...
        data,physicalNyquist,isRegular)
% Restore the v2.8 recommendation without treating its fit cutoff as Nyquist.
recommended = false;
fitMaximum = physicalNyquist;
if ~isRegular || size(data,1) < 3 || size(data,2) < 2 || ...
        ~(isfinite(physicalNyquist) && physicalNyquist > 0)
    return
end
dt = median(diff(data(:,1)));
values = data(:,2)-mean(data(:,2),'omitnan');
if ~(isfinite(dt) && dt > 0) || any(~isfinite(values))
    return
end
try
    [power,angularFrequency] = periodogram(values);
catch
    return
end
frequency = angularFrequency/(2*pi*dt);
valid = isfinite(power) & power >= 0 & ...
    isfinite(frequency) & frequency >= 0;
power = real(power(valid));
frequency = real(frequency(valid));
totalPower = sum(power);
if isempty(power) || ~(isfinite(totalPower) && totalPower > 0) || ...
        ~(isfinite(frequency(end)) && frequency(end) > 0)
    return
end
cutoffIndex = find(cumsum(power) >= 0.99*totalPower,1,'first');
if isempty(cutoffIndex) || ~(isfinite(frequency(cutoffIndex)) && ...
        frequency(cutoffIndex) > 0)
    return
end
fitMaximum = min(frequency(cutoffIndex),physicalNyquist);
recommended = fitMaximum/frequency(end) <= 0.85;
end
%% End copied source

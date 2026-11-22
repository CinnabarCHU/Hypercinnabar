function [retval,id] = analyzer(params,id)
% WaveletSpectrum.analyzer parameters: data method_sel dss pad mother param pt2 data_standardize.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wave_readGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('WaveletSpectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
method_sel = p.method_sel;
dss = p.dss;
pad = p.pad;
mother = p.mother;
param = p.param;
pt2 = p.pt2;
data_standardize = p.data_standardize;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wave_readGUI.m:L90-L103
    if method_sel == 2
        %dss = 1/12;
        % ------validate and reformat timeseries.
        [data,dt]=formatts(data);
        datax = data(:,1);
        datay = data(:,2);
        variance = std(datay)^2;
        n=size(data,1);
        sigma2=var(data(:,2));
        s0 = 2*dt;
        MaxScale=(n*.17)*2*dt; %automaxscale
        j1=round(log2(MaxScale/s0)/dss);
        lag1 = ar1nv(data(:,2));
        if any(isnan(lag1))
%% End copied source
error('Acycle:Wavelet:AR1','Automatic AR1 estimation failed.');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wave_readGUI.m:L105-L137
        end
    else
        datax = data(:,1);
        datay = data(:,2);
        variance = std(datay)^2;
        if data_standardize
            datay = (datay - mean(datay))/sqrt(variance);
        end
        n = length(datax);
        dt = mean(diff(datax));
        s0 = 2*dt;    %
        j1 = round(log2(pt2))/dss; % end
        lag1 = rhoAR1ML(datay);
    end
    % Wavelet transform:
    [wave,period,scale,coi] = wavelet(datay,dt,pad,dss,s0,j1,mother,param);
    power = (abs(wave)).^2 ;        % compute wavelet power spectrum
    
    % Significance levels: (variance=1 for the normalized datay)
    if method_sel == 2
        [signif,fft_theor] = wave_signif(1.0,dt,scale,0,lag1,-1,-1,mother,param);
        sig95 = (signif')*(ones(1,n));  % expand signif --> (J+1)x(N) array
        sig95 = power ./ (sigma2*sig95);
    else
        [signif,fft_theor] = wave_signif(datay,dt,scale,0,lag1,-1,-1,mother,param);
        sig95 = (signif')*(ones(1,n));  % expand signif --> (J+1)x(N) array
        sig95 = power ./ sig95;         % where ratio > 1, power is significant
    end
    
    % Global wavelet spectrum & significance levels:
    global_ws = variance*(sum(power')/n);   % time-average over all times
    dof = n - scale;  % the -scale corrects for padding at edges
    global_signif = wave_signif(variance,dt,scale,1,lag1,-1,dof,mother,param);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wave_readGUI.m:L139-L164
    if method_sel <3
        % Rectification of the bias in the Wavelet power spectrum with the data set
        % (Nino3.dat) given by Torrence and Compo (1998).  This code is modified
        % from wavetest.m, the example script provided by Torrence and Compo
        % (1998), to demonstrate how to rectify the bias in wavelet power spectrum.
        % This code generates Figure 4 of Liu et al. (2007).
        %
        % Yonggang Liu, 2006.4.12
        %
        % E-mail:  yliu18@gmail.com
        % http://ocgweb.marine.usf.edu/~liu/wavelet.html
        %
        % References:
        %
        % Liu, Y., X.S. Liang, and R.H. Weisberg, 2007: Rectification of the bias
        % in the wavelet power spectrum. Journal of Atmospheric and Oceanic 
        % Technology, 24(12), 2093-2102.
        %==================  Bias rectification start  =========================
         %--- divided by scales:
           for k=1:length(scale)
             powers(k,:) = power(k,:)/scale(k);
           end
           global_ws = global_ws./scale;
          power = powers;
        %==================  Bias rectification end  =========================
    end
%% End copied source
r = struct();
r.datax = datax;
r.datay = datay;
r.wave = wave;
r.period = period;
r.scale = scale;
r.coi = coi;
r.power = power;
r.sig95 = sig95;
r.global_ws = global_ws;
r.global_signif = global_signif;
r.dt = dt;
r.method_sel = method_sel;
r.variance = variance;
end

function [retval,id] = analyzer(params,id)
% PowerSpectrum.analyzer parameters: data method nw nfft.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PowerSpectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
x = p.data(:,1); y = p.data(:,2); dt = median(diff(x)); nw = p.nw;
if ~any(strcmpi(p.method,{'Multi-taper method','Periodogram','Lomb-Scargle spectrum'})), error('Acycle:Spectrum:Method','Unknown estimator.'); end
if ~(isscalar(p.nfft) && isfinite(p.nfft) && p.nfft>=1 && p.nfft==fix(p.nfft)), error('Acycle:Spectrum:NFFT','Expected an exact positive integer.'); end
[f,power] = computeSpectrum(p.method,y,x,dt,nw,p.nfft,1/(2*dt));
r = struct('frequency',f,'power',power,'dof',spectrumConfidenceDegreesOfFreedom(p.method,nw), ...
    'physicalNyquist',1/(2*dt),'nfft',p.nfft);
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

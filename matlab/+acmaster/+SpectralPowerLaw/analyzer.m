function [retval,id] = analyzer(params,id)
% SpectralPowerLaw.analyzer parameters: frequency power dof Nf.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SpectralPowerLaw-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
f = p.frequency; power = p.power; dof = p.dof; Nf = p.Nf;
[pl,loc90,loc95,loc99,g90,g95,g99] = powerLawLevels(f,power,dof,Nf);
r = struct();
r.pl = pl;
r.loc90 = loc90;
r.loc95 = loc95;
r.loc99 = loc99;
r.g90 = g90;
r.g95 = g95;
r.g99 = g99;
end

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

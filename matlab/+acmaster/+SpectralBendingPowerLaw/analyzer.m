function [retval,id] = analyzer(params,id)
% SpectralBendingPowerLaw.analyzer parameters: frequency power dof Nf.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SpectralBendingPowerLaw-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
f = p.frequency; power = p.power; dof = p.dof; Nf = p.Nf;
[bpl,loc90,loc95,loc99,g90,g95,g99] = bendingPowerLawLevels(f,power,dof,Nf);
r = struct();
r.bpl = bpl;
r.loc90 = loc90;
r.loc95 = loc95;
r.loc99 = loc99;
r.g90 = g90;
r.g95 = g95;
r.g99 = g99;
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1617-L1658
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
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/spectrum.m:L1660-L1662
        function value = stableSoftplus(value)
            value = max(value,0)+log1p(exp(-abs(value)));
        end
%% End copied source

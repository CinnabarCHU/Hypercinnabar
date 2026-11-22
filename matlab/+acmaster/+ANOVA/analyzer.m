function [retval,id] = analyzer(params,id)
% ANOVA.analyzer parameters: selectedData.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/ANOVAUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ANOVA-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
selectedData = p.selectedData;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/ANOVAUI.m:L99-L189
        [n, m] = size(selectedData);
        dof1 = m-1;
        % mean
        mean_selectedData = mean(selectedData);
        % variance
        v = var(selectedData);
        % lump all the samples
        d13 = selectedData(:);
        % variance of all samples
        d13cv = var(d13);
        % mean of all samples
        d13m = mean(d13);
        % total samples
        N = length(d13);
        dof3 = N - 1;

        % Total sum of squares
        SST = dof3 * d13cv;

        % Sum of squares within
        SSE = sum(v * (n-1));
        dof2 = N - m;
        MSE = SSE/(N-m);

        % Sum of squares among rocks
        l1 = sum(selectedData).^2/n;
        l2 = sum(d13)^2/N;
        SSA = sum(l1)-l2;
        MSA = SSA / (m - 1);

        % table
        Summary = {'among';'within';'total'};
        SumOfSquares = [SSA;SSE;SST];
        dof = [dof1; dof2; dof3];
        variance=[MSA; MSE; d13cv];

        % Create a table
        T = table(Summary,SumOfSquares,dof,variance);

        % F ratio
        F = MSA/MSE;
        % disp(['F value = ', num2str(F)])
        alpha = 0.05;
        p = 1 - alpha;
        % Reference
        X = finv(p,dof1,dof2);   
        %disp(['p = ', num2str(alpha),'; dof1 = ', num2str(dof1),'; dof2 = '...
        %    ,num2str(dof2), '; Reference = ', num2str(X)])
        %disp(' ')
        %
        PF = fcdf(F,dof1,dof2);
        %disp(['Confidence level is ',num2str(PF*100),' %'])
        % display
        if F > X
            h = 1;
            disp('h = 1, rejects the null hypothesis: all the same');
            disp('       accepts the alternative hypothesis: at least one mean is different');
        else
            h = 0;
            disp('h = 0, accepts the null hypothesis: all the same');
            disp('       rejects the alternative hypothesis: at least one mean is different');
        end

        
        multilineText = {
            ''
            'One-way analysis of variance (ANOVA) test for equal means'
            ''
            '                SumOfSquares    DF     Variance         F           pValue'
            '               --------------  ----   ----------       ---         --------'
            [' Between groups: ', sprintf('%10.6f', SSA),' ', ...
                sprintf('%5.0d', dof1),'    ', sprintf('%10.5f', MSA),'    ',  ...
            sprintf('%10.6f', F),'    ',sprintf('%10.6f', PF)]
            ['  Within groups: ', sprintf('%10.6f', SSE),' ', ...
                sprintf('%5.0d', dof2),'    ', sprintf('%10.5f', MSE)]
            ['          Total: ', sprintf('%10.6f', SST),' ', ...
                sprintf('%5.0d', dof3),'    ', sprintf('%10.5f', d13cv)]
            ''
            'CONCLUSION:'
            ''
            ['Critical F ratio (p = 0.05): ', sprintf('%10.5f', X)]
            ['           Confidence level: ', sprintf('%10.5f', PF*100) ,'%']
            ''
            ''
        }; 
            % Define the text with multiple lines
            if h == 1
                multilineText{15,1} = 'Reject the null hypothesis (equal means) at the 5% significance level.';
            else
                multilineText{15,1} = 'Accept the null hypothesis (equal means) at the 5% significance level.';
            end
%% End copied source
r = struct();
r.multilineText = multilineText;
r.F = F;
r.SSA = SSA;
r.SSE = SSE;
r.SST = SST;
end

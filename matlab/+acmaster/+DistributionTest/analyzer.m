function [retval,id] = analyzer(params,id)
% DistributionTest.analyzer parameters: data val.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/UniChi2GOFUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DistributionTest-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
val = p.val;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/UniChi2GOFUI.m:L78-L79
        data = data(:);  % force to a vector
        data = data(~isnan(data)); % remove empty cell
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/UniChi2GOFUI.m:L82-L85
        if ismember(val, ["Weibull","Lognormal","Binomial"])
            try
                pd = fitdist(data,val);
            catch
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/UniChi2GOFUI.m:L87-L92
                data = data + abs(min(data)) + eps;  % ensure data is >= 0
            end
        elseif strcmp(val, "Beta")
            try 
                pd = fitdist(data,val);
            catch
%% End copied source
                disp('Warning: Have to normalize the data to the [0,1] interval')
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/UniChi2GOFUI.m:L95-L99
            end
        elseif ismember(val, ["Exponential", "Gamma", "Poisson"])
            try 
                pd = fitdist(data,val);
            catch
%% End copied source
                disp('Warning: Have to add a constant to make all the data >= 0')
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/UniChi2GOFUI.m:L102-L129
            end
        end
        
        if ismember(val, ["Binomial"])
            data_discrete = round(data);
            N = max(data_discrete);
            binomialDist = fitdist(data_discrete, 'Binomial', 'N', N);
            [h,p,st] = chi2gof(data_discrete, 'CDF', binomialDist);
        else
            pd = fitdist(data,val);
            [h,p,st] = chi2gof(data,'CDF',pd);
        end
        
        stats = { 'Number (N)', sprintf('%10.0d',length(data)) ;
                  'Min', sprintf('%10.6f',min(data)) ;
                  'Max', sprintf('%10.6f',max(data));
                  'Mean', sprintf('%10.6f',mean(data));
                  'Median', sprintf('%10.6f',median(data));
                  '',''
                  'Chi2 statistic', sprintf('%10.6f',st.chi2stat);
                  'Degree of freedom',sprintf('%10.0d', st.df);
                  'p value',sprintf('%10.6f',p);
                  'Conclusion',''};
              if h == 0
                  stats{10,2} = ['',val,' distribution'];
              else
                  stats{10,2} = ['Not ',val,' distribution'];
              end
%% End copied source
r = struct();
r.stats = stats;
r.h = h;
r.p = p;
r.st = st;
end

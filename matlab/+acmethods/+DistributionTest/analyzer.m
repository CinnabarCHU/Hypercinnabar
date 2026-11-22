function [retval, id] = analyzer(params, id)
% DistributionTest.analyzer parameters: data val.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/UniChi2GOFUI.m#L76
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DistributionTest-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
val = p.val;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniChi2GOFUI.m:L76-L77
        data = data(:);  % force to a vector
        data = data(~isnan(data)); % remove empty cell
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniChi2GOFUI.m:L80-L83
        if ismember(val, ["Weibull","Lognormal","Binomial"])
            try
                pd = fitdist(data,val);
            catch
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniChi2GOFUI.m:L85-L91
                data = data + abs(min(data)) + eps;  % ensure data is >= 0
            end
        elseif strcmp(val, "Beta")
            try 
                pd = fitdist(data,val);
            catch
                warndlg('Warning: Have to normalize the data to the [0,1] interval')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniChi2GOFUI.m:L93-L98
            end
        elseif ismember(val, ["Exponential", "Gamma", "Poisson"])
            try 
                pd = fitdist(data,val);
            catch
                warndlg('Warning: Have to add a constant to make all the data >= 0')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/UniChi2GOFUI.m:L100-L127
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

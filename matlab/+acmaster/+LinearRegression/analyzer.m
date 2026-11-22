function [retval,id] = analyzer(params,id)
% LinearRegression.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/BivLinearRegUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('LinearRegression-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
if ~isnumeric(data) || size(data,2) ~= 2, error('Acycle:Regression:Columns','Select two numeric columns.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/BivLinearRegUI.m:L14-L14
data = data(all(isfinite(data),2),:);
%% End copied source
if size(data,1)<2, error('Acycle:Regression:Rows','At least two finite rows are required.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/univariate/BivLinearRegUI.m:L20-L44
x = data(:,1);
y = data(:,2);
p = polyfit(x,y,1);
yfit = polyval(p,x);
res = y - yfit;
ssRes = sum(res.^2);
ssTot = sum((y - mean(y)).^2);
r2 = 1 - ssRes / ssTot;
[R,P] = corrcoef(x,y);
if numel(R) >= 4
    r = R(1,2);
    pval = P(1,2);
else
    r = NaN;
    pval = NaN;
end

stats = {
    'Number (N)', sprintf('%8.0f', numel(x));
    'Intercept', sprintf('%10.6f', p(2));
    'Slope', sprintf('%10.6f', p(1));
    'R squared', sprintf('%10.6f', r2);
    'Pearson r', sprintf('%10.6f', r);
    'Pearson p', sprintf('%10.6f', pval);
    'RMSE', sprintf('%10.6f', sqrt(mean(res.^2)))};
%% End copied source
r = struct('x',x,'y',y,'coefficients',p,'fitted',yfit,'residuals',res, ...
    'rSquared',r2,'pearsonR',r,'pearsonP',pval,'stats',{stats});
end

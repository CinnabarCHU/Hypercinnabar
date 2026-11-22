function [retval,id] = analyzer(params,id)
% Detrending.analyzer parameters: data method degree(polynomial) span(smoothers).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/update_detrend_plot_fig.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Detrending-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
method = p.method;
datax=data(:,1); datay=data(:,2);
switch method
case 'raw'
trend=zeros(size(datay));
case 'mean'
dataymean=mean(datay); npts=numel(datay);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L116-L116
    datamean = dataymean * ones(npts,1);
%% End copied source
trend=datamean;
case 'linear'
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L124-L125
    sdat=polyfit(datax,datay,1);
    datalinear=datax*sdat(1)+sdat(2);
%% End copied source
trend=datalinear;
case 'quadratic'
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L132-L133
    sdat=polyfit(datax,datay,2);
    data2nd=polyval(sdat,datax);
%% End copied source
trend=data2nd;
case 'polynomial'
polynomial_value=p.degree;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L141-L142
    sdat=polyfit(datax,datay,polynomial_value);
    datamore=polyval(sdat,datax);
%% End copied source
trend=datamore;
case 'lowess'
smooth_win=p.span;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L172-L172
    datalowess=smooth(datax,datay, smooth_win,'lowess');
%% End copied source
trend=datalowess;
case 'rlowess'
smooth_win=p.span;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L180-L180
    datarlowess=smooth(datax,datay, smooth_win,'rlowess');
%% End copied source
trend=datarlowess;
case 'loess'
smooth_win=p.span;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L188-L188
    dataloess=smooth(datax,datay, smooth_win,'loess');
%% End copied source
trend=dataloess;
case 'rloess'
smooth_win=p.span;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L196-L196
    datarloess=smooth(datax,datay, smooth_win,'rloess');
%% End copied source
trend=datarloess;
case 'eemd'
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L151-L152
    [imfs,~,~] = emd(datay);
    [~, ncol] = size(imfs);
%% End copied source
    q=struct('y',datay','goal',ncol+1,'ens',50,'nos',.2);
    s=acmaster.eemd.analyzer(q); imfs=s.modes;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L159-L160
    imfs = imfs';
    dataEMDres = imfs(:,end);
%% End copied source
    trend=dataEMDres;
otherwise, error('Acycle:Detrend:Method','Unknown trend model.'); end
residual=datay-trend;
r = struct();
r.datax = datax;
r.datay = datay;
r.trend = trend;
r.residual = residual;
r.method = method;
end

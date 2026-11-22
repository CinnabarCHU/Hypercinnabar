function [retval,id] = plotter(params,id)
% Detrending.plotter parameters: datax datay trend method.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/update_detrend_plot_fig.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Detrending-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
datax = p.datax;
datay = p.datay;
trend = p.trend;
method = p.method;
figure;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L101-L101
plot(datax,datay,'-k');
%% End copied source
hold on;
switch method
case 'mean'
datamean=trend;
dataymean=trend(1);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L117-L117
    hlin = line([min(datax),max(datax)],[dataymean,dataymean]);
%% End copied source
case 'linear'
datalinear=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L126-L126
    plot(datax,datalinear,'-y','Linewidth',2)
%% End copied source
case 'quadratic'
data2nd=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L134-L134
    plot(datax,data2nd,':r','Linewidth',2)
%% End copied source
case 'polynomial'
datamore=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L143-L143
    plot(datax,datamore,'b-.','Linewidth',2)
%% End copied source
case 'lowess'
datalowess=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L173-L173
    plot(datax,datalowess,'-g','Linewidth',2)
%% End copied source
case 'rlowess'
datarlowess=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L181-L181
    plot(datax,datarlowess,':b','Linewidth',2)
%% End copied source
case 'loess'
dataloess=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L189-L189
    plot(datax,dataloess,'--r','Linewidth',2)
%% End copied source
case 'rloess'
datarloess=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L197-L197
    plot(datax,datarloess,'--m','Linewidth',2)
%% End copied source
case 'eemd'
    dataEMDres=trend;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_detrend_plot_fig.m:L162-L162
    plot(datax,dataEMDres,'-r','Linewidth',4)
%% End copied source
end
hold off;
r=[];
end

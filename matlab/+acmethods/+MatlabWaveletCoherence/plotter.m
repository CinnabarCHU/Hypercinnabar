function [retval, id] = plotter(params, id)
% MatlabWaveletCoherence.plotter parameters: result plot_series plot_swap plot_2d plot_linelog plot_colorgrid plot_colormap plot_flipx plot_flipy plot_phase plot_coi plot_sl plot_log2pow pt1 pt2 Yticks unit unit_type wtcthreshold.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wavecoh_readGUI.m#L274
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wavecoh_update_plots.m#L12
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MatlabWaveletCoherence-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
handles=struct('unit',p.unit,'unit_type',p.unit_type,'lang_choice',0,'main_unit_selection',0,'MonZoom',1);
handles.lang_id={'menu129','wave28','main34','main23','main21','main24','main12'};
handles.lang_var={'Wavelet coherence','Cross-wavelet','Unit','Depth','Time','Value','Series'};
handles.figwave=figure('Name','Acycle: Wavelet coherence','Color','white');
handles.waveletGUIfig=handles.figwave;
plot_series = p.plot_series;
plot_swap = p.plot_swap;
plot_2d = p.plot_2d;
plot_linelog = p.plot_linelog;
plot_colorgrid = p.plot_colorgrid;
plot_colormap = p.plot_colormap;
plot_flipx = p.plot_flipx;
plot_flipy = p.plot_flipy;
plot_phase = p.plot_phase;
plot_coi = p.plot_coi;
plot_sl = p.plot_sl;
plot_log2pow = p.plot_log2pow;
pt1 = p.pt1;
pt2 = p.pt2;
Yticks = p.Yticks;
datax=p.result.datax;
dat1y=p.result.dat1y;
dat2y=p.result.dat2y;
wcoh=p.result.wcoh;
wcs=p.result.wcs;
period=p.result.period;
coi=p.result.coi;
method_sel=1;
wtcthreshold=p.wtcthreshold;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavecoh_readGUI.m:L274-L274
xlim = [min(datax),max(datax)];
%% End copied source
wavecoh_update_plots;
r=[];
end

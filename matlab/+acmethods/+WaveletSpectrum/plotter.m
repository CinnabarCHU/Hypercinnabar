function [retval, id] = plotter(params, id)
% WaveletSpectrum.plotter parameters: datax dt period power coi sig95 method_sel variance plot_2d plot_base plot_coi plot_colorgrid plot_colormap plot_flipx plot_flipy plot_linelog plot_log2pow plot_sl plot_z pt1 pt2 Yticks unit unit_type.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wave_update_wavelet.m#L11
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wave_readGUI.m#L228
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('WaveletSpectrum-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
datax = p.datax;
dt = p.dt;
period = p.period;
power = p.power;
coi = p.coi;
sig95 = p.sig95;
method_sel = p.method_sel;
variance = p.variance;
plot_2d = p.plot_2d;
plot_base = p.plot_base;
plot_coi = p.plot_coi;
plot_colorgrid = p.plot_colorgrid;
plot_colormap = p.plot_colormap;
plot_flipx = p.plot_flipx;
plot_flipy = p.plot_flipy;
plot_linelog = p.plot_linelog;
plot_log2pow = p.plot_log2pow;
plot_sl = p.plot_sl;
plot_z = p.plot_z;
pt1 = p.pt1;
pt2 = p.pt2;
Yticks=p.Yticks;
unit = p.unit;
unit_type = p.unit_type;
handles=struct('lang_choice',0,'main_unit_selection',0,'unit',unit,'unit_type',unit_type);
handles.lang_var={};
sigma2=variance;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wave_readGUI.m:L228-L241
if method_sel == 3
    powermax = floor(log2(max(power(:))));
    % levels
    plot_level_vector = -1*powermax:powermax;
    power(power< plot_base^(-1*powermax)) = plot_base^(-1*powermax);
elseif method_sel < 3
    powermax = floor(log2(max(power(:))));
    powermin = floor(log2(min(power(:))));
    plot_level_vector = powermin:powermax;
end
%plot_level_vector = -1:powermax;
levels = plot_base.^plot_level_vector;
% plot
xlim = [min(datax),max(datax)];
%% End copied source
figure;
wave_update_wavelet;
r=[];
end

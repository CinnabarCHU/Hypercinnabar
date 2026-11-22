function [retval, id] = plotter(params, id)
% spectralmoments.plotter parameters: depth uf Bw Bwtrend sr unit.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/SpectralMomentsGUI.m#L260
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('spectralmoments-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
depth = p.depth;
uf = p.uf;
Bw = p.Bw;
Bwtrend = p.Bwtrend;
sr = p.sr;
unit = p.unit;
handles.unit=unit;
if isempty(sr)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SpectralMomentsGUI.m:L260-L263
    figure; 
    set(gcf,'color','w');
    plot(depth,uf,'r-',depth,Bw,'b-.');
    xlabel(handles.unit); ylabel('Frequency (cycles/m)'); legend('\mu_f','B')
%% End copied source
else
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SpectralMomentsGUI.m:L275-L281
    figure; 
    set(gcf,'color','w');
    plot(depth,uf,'r-',depth,Bw,'b-.',depth,Bwtrend,'g');
    xlabel(handles.unit); ylabel('Frequency (cycles/m)'); legend('\mu_f','B','B trend')
    figure; 
    set(gcf,'color','w');
    plot(depth, sr); xlabel('Depth (m)'); ylabel('Sed. rate (cm/kyr)');
%% End copied source
end
r=[];
end

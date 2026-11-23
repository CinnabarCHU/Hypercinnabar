function [fig,handles,s] = bispectralFigure(s,varargin)
% The native master window needs live objects. The Core journal stores their settings.
style = struct('settings',struct(varargin{:}));
before = findall(groot,'Type','figure');
s = accli.replot(s,style);
figs = findall(groot,'Type','figure');
figs = figs(~ismember(figs,before));
complete = arrayfun(@(f)isequal(getappdata(f,'BispectralPlotComplete'),true),figs);
fig = figs(complete);
if ~isscalar(fig), error('Acycle:Bispectral:Figure','Expected one completed bispectral figure.'); end
handles = getappdata(fig,'AcycleBispectralHandles');
end

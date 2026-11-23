function h = filterPreview(h,p,style)
% Keep both original axes and the export data associated with the last successful fit.
s = h.bandpassSession;
names = fieldnames(p);
same = all(cellfun(@(key)isfield(s.params,key) && isequaln(s.params.(key),p.(key)),names));
if ~same, s = accli.rerun(s,p); end
style.panel = 1;
s = accli.replot(s,style,h.ft_axes3);
style.panel = 2;
s = accli.replot(s,style,h.ft_axes4);
h.bandpassSession = s;
setappdata(ancestor(h.ft_axes3,'figure'),'AcycleAnalysis',s);
h.data_filterout = s.res.data_filterout;
if isfield(s.res,'ifaze'), h.ifaze = s.res.ifaze; h.ifreq = s.res.ifreq; end
end

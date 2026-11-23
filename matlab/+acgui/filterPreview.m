function h = filterPreview(h,p,style)
% Keep both original axes and the export data associated with the last successful fit.
s = h.bandpassSession;
names = fieldnames(p);
same = all(cellfun(@(key)isfield(s.params,key) && isequaln(s.params.(key),p.(key)),names));
if ~same
    changed = p;
    for k = 1:numel(names)
        key = names{k};
        if isfield(s.params,key) && isequaln(s.params.(key),p.(key)), changed = rmfield(changed,key); end
    end
    s = accli.rerun(s,changed);
end
originalChoices = s.explicit.plt;
for k = reshape(fieldnames(style),1,[])
    if ~isfield(s.plt,k{1}) || ~isequaln(style.(k{1}),s.plt.(k{1})), originalChoices.(k{1}) = style.(k{1}); end
end
style.panel = 'fft';
s = accli.replot(s,style,h.ft_axes3);
s.panels.fft = s.ids.plotter;
style.panel = 'mtm';
s = accli.replot(s,style,h.ft_axes4);
s.panels.mtm = s.ids.plotter;
s.plt = rmfield(s.plt,'panel');
s.explicit.plt = originalChoices;
h.bandpassSession = s;
setappdata(ancestor(h.ft_axes3,'figure'),'AcycleAnalysis',s);
h.data_filterout = s.res.data_filterout;
if isfield(s.res,'ifaze'), h.ifaze = s.res.ifaze; h.ifreq = s.res.ifreq; end
end

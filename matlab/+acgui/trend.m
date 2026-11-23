function [h,r] = trend(h,method,degree,span)
% Each selected trend has a separate analysis. The original window can overlay them.
if ~isfield(h,'trendSessions'), h.trendSessions = struct(); end
p = struct('method',method);
if strcmp(method,'polynomial'), p.degree = degree; end
if ismember(method,{'lowess','rlowess','loess','rloess'}), p.span = span; end
if isfield(h.trendSessions,method)
    s = h.trendSessions.(method);
    keys = fieldnames(p);
    if ~all(cellfun(@(k)isequaln(p.(k),s.params.(k)),keys)), s = accli.rerun(s,p); end
else
    s = accli.run('menu_prewhiten',h.current_data,'Params',p);
end
h.trendSessions.(method) = s;
r = s.res;
setappdata(h.output,'AcycleAnalysis',s);
end

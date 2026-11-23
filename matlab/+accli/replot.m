function s = replot(s,changes,target)
% Redraw a successful result without running its Analyzer.
if nargin < 2, changes = struct(); end
if nargin < 3, target = []; end
if isfield(changes,'operation'), error('Acycle:CLI:Style','A style cannot change the analysis.'); end
style = acMenuMerge(s.plt,changes);
id = acMenuNewId();
accore.source(id,struct('helper',s.ids.helper,'analyzer',s.ids.analyzer,'plotter',s.ids.plotter));
accore.run(s.tag,'plotter',style,'dat',s.dat,'params',s.params,'res',s.res,'target',target,'id',id);
s.plt = style; s.ids.plotter = id; s.explicit.plt = acMenuMerge(s.explicit.plt,changes);
end

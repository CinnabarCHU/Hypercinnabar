function next = apply(s,input,varargin)
% Keep explicit choices while letting the Helper recompute data-dependent defaults.
next = accli.run(s.tag,input,'Operation',s.operation,'Params',s.explicit.params,'Plt',s.explicit.plt,varargin{:});
end

function retval = acMenuLeadlag_analyzer(params,varargin)
% Timeseries > Lead-lag Relationship (menu_leadlag). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_leadlag','analyzer',params,varargin{:});
end

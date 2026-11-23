function retval = acMenuCorrelation_analyzer(params,varargin)
% Timeseries > Stratigraphic Correlation (menu_correlation). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_correlation','analyzer',params,varargin{:});
end

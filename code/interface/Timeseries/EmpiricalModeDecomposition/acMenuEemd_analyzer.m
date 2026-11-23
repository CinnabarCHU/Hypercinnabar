function retval = acMenuEemd_analyzer(params,varargin)
% Timeseries > Empirical Mode Decomposition > Ensemble Empirical Mode Decomposition (EEMD) (menu_eemd). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_eemd','analyzer',params,varargin{:});
end

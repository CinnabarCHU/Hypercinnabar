function retval = acMenuSwa_analyzer(params,varargin)
% Timeseries > Spectral Analysis (SWA) (menu_swa). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_swa','analyzer',params,varargin{:});
end

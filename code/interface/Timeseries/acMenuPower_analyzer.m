function retval = acMenuPower_analyzer(params,varargin)
% Timeseries > Spectral Analysis (menu_power). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_power','analyzer',params,varargin{:});
end

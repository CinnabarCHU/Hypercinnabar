function retval = acMenuDynos_analyzer(params,varargin)
% Timeseries > Sedimentary Noise Model > Dynamic noise after orbital tuning (DYNOT) (menu_dynos). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_dynos','analyzer',params,varargin{:});
end

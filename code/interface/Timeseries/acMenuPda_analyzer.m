function retval = acMenuPda_analyzer(params,varargin)
% Timeseries > Power Decomposition Analysis (menu_pda). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_pda','analyzer',params,varargin{:});
end

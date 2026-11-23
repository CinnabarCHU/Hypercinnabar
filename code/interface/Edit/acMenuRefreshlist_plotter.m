function retval = acMenuRefreshlist_plotter(varargin)
% Edit > Refresh (menu_refreshlist). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_refreshlist','plotter',varargin{:});
end

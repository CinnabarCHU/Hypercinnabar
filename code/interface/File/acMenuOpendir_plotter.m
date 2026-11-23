function retval = acMenuOpendir_plotter(varargin)
% File > Open Directory (menu_opendir). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_opendir','plotter',varargin{:});
end

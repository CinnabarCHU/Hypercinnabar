function retval = acMenuSavefig_plotter(varargin)
% File > Save *.AC.fig (menu_savefig). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_savefig','plotter',varargin{:});
end

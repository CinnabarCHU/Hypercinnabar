function retval = acMenuCut_plotter(varargin)
% Edit > Cut (menu_cut). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_cut','plotter',varargin{:});
end

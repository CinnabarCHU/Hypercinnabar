function retval = acMenuPaste_plotter(varargin)
% Edit > Paste (menu_paste). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_paste','plotter',varargin{:});
end

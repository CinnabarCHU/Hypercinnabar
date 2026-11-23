function retval = acMenuFolder_plotter(varargin)
% File > New Folder (menu_folder). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_folder','plotter',varargin{:});
end

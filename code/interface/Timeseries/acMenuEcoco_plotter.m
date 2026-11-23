function retval = acMenuEcoco_plotter(varargin)
% Timeseries > Correlation Coefficient (COCO/eCOCO) (menu_ecoco). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_ecoco','plotter',varargin{:});
end

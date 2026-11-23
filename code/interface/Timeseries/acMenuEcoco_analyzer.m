function retval = acMenuEcoco_analyzer(params,varargin)
% Timeseries > Correlation Coefficient (COCO/eCOCO) (menu_ecoco). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_ecoco','analyzer',params,varargin{:});
end

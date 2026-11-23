function retval = acMenuRgb2lab_analyzer(params,varargin)
% Math > Image > RGB to CIE Lab (menu_rgb2lab). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_rgb2lab','analyzer',params,varargin{:});
end

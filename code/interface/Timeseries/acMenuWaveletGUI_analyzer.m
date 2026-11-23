function retval = acMenuWaveletGUI_analyzer(params,varargin)
% Timeseries > Wavelet (menu_waveletGUI). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_waveletGUI','analyzer',params,varargin{:});
end

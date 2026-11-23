function retval = acMenuLyapunov_plotter(varargin)
% Timeseries > Sedimentary Noise Model > Lyapunov exponent (menu_lyapunov). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_lyapunov','plotter',varargin{:});
end

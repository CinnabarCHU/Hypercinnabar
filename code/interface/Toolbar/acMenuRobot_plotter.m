function retval = acMenuRobot_plotter(varargin)
% Toolbar > Mini-Robot (push_robot). See acMenuCatalog for available operations.
retval = acMenuInvoke('push_robot','plotter',varargin{:});
end

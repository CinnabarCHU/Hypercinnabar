function retval = acMenuRobot_helper(varargin)
% Toolbar > Mini-Robot (push_robot). See acMenuCatalog for available operations.
retval = acMenuInvoke('push_robot','helper',varargin{:});
end

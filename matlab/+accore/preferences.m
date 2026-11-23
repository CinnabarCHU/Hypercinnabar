function value = preferences(action,varargin)
% The old language selector and the master settings window share one preference file.
guard = accompat.masterPath(); %#ok<NASGU>
value = ac_user_settings(action,varargin{:});
end

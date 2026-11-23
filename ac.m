function varargout = ac(varargin)
% Open the code-only Acycle desktop.
setup_acycle;
[varargout{1:nargout}] = acgui.desktop(varargin{:});
end

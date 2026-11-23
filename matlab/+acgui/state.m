function value = state(object,varargin)
% All controls in a window share the state of their owning figure.
fig = ancestor(object,'figure','toplevel');
if isgraphics(object,'figure'), fig = object; end
if isempty(fig), error('Acycle:GUI:Owner','A live figure is required.'); end
if nargin == 2, setappdata(fig,'AcycleWindowState',varargin{1}); end
value = getappdata(fig,'AcycleWindowState');
end

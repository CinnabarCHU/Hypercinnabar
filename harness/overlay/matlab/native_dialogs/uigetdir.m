function varargout=uigetdir(varargin)
% Scoped native-job shim: responses are supplied explicitly in the request.
[varargout{1:nargout}]=acycle_native_dialog('uigetdir',varargin{:});
end

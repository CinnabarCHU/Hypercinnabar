function varargout=inputdlg(varargin)
% Scoped native-job shim: responses are supplied explicitly in the request.
[varargout{1:nargout}]=acycle_native_dialog('inputdlg',varargin{:});
end

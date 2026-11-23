function name = share(requested)
% Explicitly share the current desktop and report its actual Engine name.
if nargin < 1, requested = 'AcycleDesktop'; end
if matlab.engine.isEngineShared()
    name = matlab.engine.engineName();
    return
end
if ~isvarname(requested), error('Acycle:GUI:EngineName','Use a valid MATLAB identifier.'); end
matlab.engine.shareEngine(requested);
name = matlab.engine.engineName();
end

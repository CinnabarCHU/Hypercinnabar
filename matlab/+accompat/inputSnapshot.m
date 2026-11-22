function params = inputSnapshot(params)
% Preserve the exact bytes passed to file-based methods for later replay.
if isfield(params,'input_bytes'), return; end
if ~isstruct(params) || ~isfield(params,'inputfile') || ~(ischar(params.inputfile) || isstring(params.inputfile)), return; end
[fid,msg]=fopen(params.inputfile,'rb');
if fid<0, params.input_error=msg; return; end
cleanup=onCleanup(@() fclose(fid));
params.input_bytes=fread(fid,Inf,'*uint8');
end

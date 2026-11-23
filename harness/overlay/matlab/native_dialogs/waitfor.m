function waitfor(varargin)
% Do not silently skip asynchronous GUI state transitions.
error('Harness:InteractionRequired','waitfor requires asynchronous GUI interaction; use an explicit calculation entrypoint.');
end

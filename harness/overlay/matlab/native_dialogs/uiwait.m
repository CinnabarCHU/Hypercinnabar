function uiwait(varargin)
% Do not silently skip asynchronous GUI state transitions.
error('Harness:InteractionRequired','uiwait requires asynchronous GUI interaction; use an explicit calculation entrypoint.');
end

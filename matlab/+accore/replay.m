function [value,newId] = replay(id)
% The recorded menu executor uses the exact operation, arguments and initial RNG.
[value,newId] = aclog.replay(id);
end

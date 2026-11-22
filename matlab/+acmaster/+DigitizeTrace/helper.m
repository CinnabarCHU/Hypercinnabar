function [retval,id] = helper(params,id)
% DigitizeTrace.helper parameters: image seeds calibration.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/plotdigitizer.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DigitizeTrace-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = p;
r.mode = 'Loose';
r.existingPixels = zeros(0,2);
end

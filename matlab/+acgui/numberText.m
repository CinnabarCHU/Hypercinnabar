function text = numberText(value)
% Keep the historical short display when it round-trips to the original double.
text = num2str(value);
if ~isequaln(str2double(text),value)
    text = jsonencode(value);
    if ~isequaln(str2double(text),value), text = sprintf('%.17g',value); end
end
end

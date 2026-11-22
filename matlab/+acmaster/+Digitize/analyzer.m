function [retval,id] = analyzer(params,id)
% Digitize.analyzer parameters: pixels calibration.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/plotdigitizer.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Digitize-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
cal = p.calibration;
if ~isequal(size(cal.pixels),[4 2]) || numel(cal.limits)~=4
    error('Acycle:Digitize:Calibration','Supply four axis clicks and four axis limits.');
end
app = struct();
for k = 1:4
    app.(sprintf('x0%d',k-1)) = cal.pixels(k,1);
    app.(sprintf('y0%d',k-1)) = cal.pixels(k,2);
end
if abs(app.x01-app.x00)<eps || abs(app.y03-app.y02)<eps
    error('Acycle:Digitize:Calibration','Calibration axes have zero pixel length.');
end
app.EditXStart.Value = num2str(cal.limits(1),17);
app.EditXEnd.Value = num2str(cal.limits(2),17);
app.EditYStart.Value = num2str(cal.limits(3),17);
app.EditYEnd.Value = num2str(cal.limits(4),17);
app.RadioXLinear.Value = ~cal.logX;
app.RadioYLinear.Value = ~cal.logY;
[x,y] = convertPixelBatchToValue(app,p.pixels(:,1),p.pixels(:,2));
r = [x,y];
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L892-L912
        function [xv,yv] = convertPixelBatchToValue(app, x, y)
            xmin = str2double(app.EditXStart.Value);
            xmax = str2double(app.EditXEnd.Value);
            ymin = str2double(app.EditYStart.Value);
            ymax = str2double(app.EditYEnd.Value);

            x = double(x(:));
            y = double(y(:));

            if app.RadioXLinear.Value
                xv = (xmax - xmin)*(x - app.x00)/(app.x01 - app.x00) + xmin;
            else
                xv = 10.^((log10(xmax) - log10(xmin))*(x - app.x00)/(app.x01 - app.x00) + log10(xmin));
            end

            if app.RadioYLinear.Value
                yv = (ymax - ymin)*(y - app.y02)/(app.y03 - app.y02) + ymin;
            else
                yv = 10.^((log10(ymax) - log10(ymin))*(log10(y) - log10(app.y02))/(log10(app.y03) - log10(app.y02)) + log10(ymin));
            end
        end
%% End copied source

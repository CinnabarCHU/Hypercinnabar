function [retval,id] = analyzer(params,id)
% DigitizeTrace.analyzer parameters: image seeds calibration mode existingPixels.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/plotdigitizer.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DigitizeTrace-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function [r,status] = execute(p)
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
if ~any(strcmpi(p.mode,{'Loose','Strict'})), error('Acycle:Digitize:Mode','Expected Strict or Loose.'); end
app.AutoMode.Value = p.mode;
app.applyPlotAreaMask = @(bw) applyPlotAreaMask(app,bw);
app.connectedComponentFromSeed = @(bw,x,y) connectedComponentFromSeed([],bw,x,y);
app.tableDatai = [(1:size(p.existingPixels,1))',p.existingPixels];
gray = toGray([],p.image);
bw = buildCurveMask(app,gray);
n = size(p.seeds,1);
segments = cell(n,1);
values = cell(n,1);
reasons = cell(n,1);
for i = 1:n
    sx = p.seeds(i,1); sy = p.seeds(i,2);
    [sx,sy,found] = snapSeedToMask([],bw,round(sx),round(sy),18);
    if ~found, [sx,sy,found] = snapSeedToDark([],gray,round(sx),round(sy),18); end
    if ~found, reasons{i} = 'no_seed'; continue; end
    [pts,reasons{i}] = traceSeedCurve(app,bw,gray,sx,sy);
    if size(pts,1)<8, reasons{i} = 'too_short'; continue; end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L554-L558
                pts = unique(pts,'rows','stable');
                if size(pts,1) > 1
                    keep = [true; hypot(diff(pts(:,1)),diff(pts(:,2))) >= 1];
                    pts = pts(keep,:);
                end
%% End copied source
    pts = removeExistingPixels(app,pts,2.0);
    if isempty(pts), reasons{i} = 'already_digitized'; continue; end
    [x,y] = convertPixelBatchToValue(app,pts(:,1),pts(:,2));
    app.tableDatai = [app.tableDatai;[(1:size(pts,1))',pts]];
    segments{i} = pts; values{i} = [x,y];
end
r = struct('segments',{segments},'pixels',vertcat(segments{:}),'data',vertcat(values{:}),'reasons',{reasons});
status = 'done';
if isempty(r.pixels), r = []; status = 'cancelled';
elseif any(cellfun(@isempty,segments)), status = 'incomplete'; end
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L588-L597
        function gray = toGray(~, I)
            if ndims(I) == 3
                gray = 0.2989*double(I(:,:,1)) + 0.5870*double(I(:,:,2)) + 0.1140*double(I(:,:,3));
            else
                gray = double(I);
            end
            if max(gray(:)) > 0
                gray = gray ./ max(gray(:));
            end
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L599-L613
        function bw = buildCurveMask(app, gray)
            % Black-pixel extraction for BW/near-BW plots.
            v = sort(gray(:));
            if strcmpi(app.AutoMode.Value,'Strict')
                q = 0.24;
            else
                q = 0.35;
            end
            idx = max(1, min(numel(v), round(q*numel(v))));
            t = v(idx);
            % Clamp to robust dark threshold range.
            t = min(max(t,0.05),0.45);
            bw = gray <= t;
            bw = app.applyPlotAreaMask(bw);
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L615-L710
        function [pts, stopReason] = traceSeedCurve(app, bw, gray, sx, sy)
            % Trace one curve by extracting seed-connected dark component,
            % then selecting one y per x with continuity constraints.
            [comp, okComp] = app.connectedComponentFromSeed(bw, sx, sy);
            if ~okComp
                pts = zeros(0,2);
                stopReason = 'no_component';
                return
            end

            [yy,xx] = find(comp);
            if isempty(xx)
                pts = zeros(0,2);
                stopReason = 'empty_component';
                return
            end

            if strcmpi(app.AutoMode.Value,'Strict')
                maxJump = 5;
                darkW = 0.18;
            else
                maxJump = 7;
                darkW = 0.12;
            end

            rx = max(xx) - min(xx) + 1;
            ry = max(yy) - min(yy) + 1;
            verticalMajor = ry > 1.25 * rx;

            pts = zeros(0,2);
            if verticalMajor
                uy = sort(unique(yy),'ascend');
                prevX = sx;
                lastY = uy(1)-1;
                for i = 1:numel(uy)
                    y = uy(i);
                    if y - lastY > 3 && strcmpi(app.AutoMode.Value,'Strict')
                        break
                    end
                    xs = xx(yy == y);
                    if isempty(xs), continue; end
                    c = abs(double(xs) - double(prevX)) + darkW*255*gray(sub2ind(size(gray),repmat(y,size(xs)),xs));
                    [cMin, kMin] = min(c);
                    xSel = xs(kMin);
                    if i > 1 && abs(double(xSel)-double(prevX)) > maxJump
                        if strcmpi(app.AutoMode.Value,'Strict')
                            break
                        else
                            [~,k2] = min(abs(double(xs)-double(prevX)));
                            xSel = xs(k2);
                        end
                    end
                    if cMin > maxJump*2 && strcmpi(app.AutoMode.Value,'Strict')
                        break
                    end
                    pts(end+1,:) = [xSel,y]; %#ok<AGROW>
                    prevX = xSel;
                    lastY = y;
                end
                stopReason = 'ok_v';
            else
                ux = sort(unique(xx),'ascend');
                prevY = sy;
                lastX = ux(1)-1;
                for i = 1:numel(ux)
                    x = ux(i);
                    if x - lastX > 3 && strcmpi(app.AutoMode.Value,'Strict')
                        break
                    end
                    ys = yy(xx == x);
                    if isempty(ys), continue; end
                    c = abs(double(ys) - double(prevY)) + darkW*255*gray(sub2ind(size(gray),ys,repmat(x,size(ys))));
                    [cMin, kMin] = min(c);
                    ySel = ys(kMin);
                    if i > 1 && abs(double(ySel)-double(prevY)) > maxJump
                        if strcmpi(app.AutoMode.Value,'Strict')
                            break
                        else
                            [~,k2] = min(abs(double(ys)-double(prevY)));
                            ySel = ys(k2);
                        end
                    end
                    if cMin > maxJump*2 && strcmpi(app.AutoMode.Value,'Strict')
                        break
                    end
                    pts(end+1,:) = [x,ySel]; %#ok<AGROW>
                    prevY = ySel;
                    lastX = x;
                end
                stopReason = 'ok_h';
            end

            if size(pts,1) < 3
                stopReason = 'short';
            end
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L712-L730
        function [sx,sy,ok] = snapSeedToDark(~, gray, sx, sy, rad)
            [h,w] = size(gray);
            x0 = max(1,sx-rad); x1 = min(w,sx+rad);
            y0 = max(1,sy-rad); y1 = min(h,sy+rad);
            patch = gray(y0:y1,x0:x1);
            if isempty(patch)
                ok = false;
                return
            end
            [v, k] = min(patch(:));
            if isempty(v) || v > 0.55
                ok = false;
                return
            end
            [yy,xx] = ind2sub(size(patch),k);
            sx = x0 + xx - 1;
            sy = y0 + yy - 1;
            ok = true;
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L732-L767
        function [comp, ok] = connectedComponentFromSeed(~, bw, sx, sy)
            [h,w] = size(bw);
            comp = false(h,w);
            ok = false;
            if sx < 1 || sx > w || sy < 1 || sy > h || ~bw(sy,sx)
                return
            end

            % BFS flood-fill (8-connected)
            q = zeros(numel(bw),2);
            head = 1; tail = 1;
            q(tail,:) = [sy,sx];
            comp(sy,sx) = true;
            nbr = [-1 -1; -1 0; -1 1; 0 -1; 0 1; 1 -1; 1 0; 1 1];
            maxNodes = min(numel(bw), 2e6);
            nNodes = 1;

            while head <= tail
                y = q(head,1); x = q(head,2); head = head + 1;
                for k = 1:8
                    y2 = y + nbr(k,1);
                    x2 = x + nbr(k,2);
                    if y2 >= 1 && y2 <= h && x2 >= 1 && x2 <= w && bw(y2,x2) && ~comp(y2,x2)
                        tail = tail + 1;
                        q(tail,:) = [y2,x2];
                        comp(y2,x2) = true;
                        nNodes = nNodes + 1;
                        if nNodes >= maxNodes
                            ok = true;
                            return
                        end
                    end
                end
            end
            ok = nNodes > 0;
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L840-L856
        function [sx,sy,ok] = snapSeedToMask(~, bw, sx, sy, rad)
            [h,w] = size(bw);
            x0 = max(1,sx-rad); x1 = min(w,sx+rad);
            y0 = max(1,sy-rad); y1 = min(h,sy+rad);
            [yy,xx] = find(bw(y0:y1,x0:x1));
            if isempty(xx)
                ok = false;
                return
            end
            xx = xx + x0 - 1;
            yy = yy + y0 - 1;
            d2 = (xx-sx).^2 + (yy-sy).^2;
            [~,k] = min(d2);
            sx = xx(k);
            sy = yy(k);
            ok = true;
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L858-L875
        function bw = applyPlotAreaMask(app, bw)
            % Use axis calibration to constrain to plotting area and reduce false picks.
            xMin = floor(min([app.x00,app.x01,app.x02,app.x03]));
            xMax = ceil(max([app.x00,app.x01,app.x02,app.x03]));
            yMin = floor(min([app.y00,app.y01,app.y02,app.y03]));
            yMax = ceil(max([app.y00,app.y01,app.y02,app.y03]));
            [h,w] = size(bw);
            pad = 12;
            xMin = max(1,xMin-pad); xMax = min(w,xMax+pad);
            yMin = max(1,yMin-pad); yMax = min(h,yMax+pad);
            mask = false(h,w);
            if xMin < xMax && yMin < yMax
                mask(yMin:yMax,xMin:xMax) = true;
            else
                mask(:) = true;
            end
            bw = bw & mask;
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L877-L890
        function pts = removeExistingPixels(app, pts, dMin)
            if isempty(app.tableDatai)
                return
            end
            old = app.tableDatai(:,2:3);
            keep = true(size(pts,1),1);
            for i = 1:size(pts,1)
                dp = old - pts(i,:);
                if any(hypot(dp(:,1),dp(:,2)) <= dMin)
                    keep(i) = false;
                end
            end
            pts = pts(keep,:);
        end
%% End copied source

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

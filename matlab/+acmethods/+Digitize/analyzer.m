function [retval, id] = analyzer(params, id)
% Digitize.analyzer parameters: pixels x00 x01 y02 y03 xmin xmax ymin ymax scale1 scale2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DataExtractML.m#L436
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Digitize-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
pixels = p.pixels;
x00 = p.x00;
x01 = p.x01;
y02 = p.y02;
y03 = p.y03;
xmin = p.xmin;
xmax = p.xmax;
ymin = p.ymin;
ymax = p.ymax;
scale1 = p.scale1;
scale2 = p.scale2;
tableData=cell(size(pixels,1),3); tableDatai=tableData;
for i=1:size(pixels,1)
    x=pixels(i,1); y=pixels(i,2);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DataExtractML.m:L436-L452
        if scale1 == 1
            xx = (xmax - xmin)*(x - x00)/(x01 - x00) + xmin;
        else
            xx = 10^((log10(xmax) - log10(xmin))*(x - x00)/(x01 - x00) + log10(xmin));
        end
        if scale2 == 1
            yy = (ymax - ymin)*(y - y02)/(y03 - y02) + ymin;
        else
            yy = 10^((log10(ymax) - log10(ymin))*(log10(y) - log10(y02))/(log10(y03) - log10(y02)) + log10(ymin));
        end
        tableData{i, 1} = i;
        tableData{i, 2} = xx;
        tableData{i, 3} = yy;
        
        tableDatai{i, 1} = i;
        tableDatai{i, 2} = x;
        tableDatai{i, 3} = y;
%% End copied source
end
r = struct();
r.tableData = tableData;
r.tableDatai = tableDatai;
end

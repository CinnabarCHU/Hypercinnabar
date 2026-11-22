function [retval,id] = analyzer(params,id)
% ColumnManipulation.analyzer parameters: dataCell colman1.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/column_manipulateGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ColumnManipulation-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
dataCell = p.dataCell;
colman1 = p.colman1;
n=numel(dataCell);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/column_manipulateGUI.m:L40-L45
    % Merge data and insert blank columns
    mergedData = [];
    dataMan = [];
    for i = 1:n
        mergedData = [mergedData, dataCell{i}, nan(size(dataCell{i}, 1), 1)];  % Add a column of NaNs as blank
    end
%% End copied source
k=size(colman1,1);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/column_manipulateGUI.m:L203-L203
        dataMan = zeros(length(mergedData),1);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/column_manipulateGUI.m:L222-L227
        if k > 0
            % add col * weight
            for j = 1:k
                dataMan1 = mergedData(:, colman1(j,1)) .* colman1(j,2);
                dataMan = dataMan + dataMan1;
            end
%% End copied source
end
series=[mergedData(:,1),dataMan];
r = struct();
r.mergedData = mergedData;
r.dataMan = dataMan;
r.series = series;
end

function [retval,id] = analyzer(params,id)
% Clipping.analyzer parameters: data clip_value clip_high clip_set.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Clipping-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
clip_value = p.clip_value;
clip_high = p.clip_high;
clip_set = p.clip_set;
if ~ismember(clip_set,0:2), error('Acycle:Clipping:Mode','Expected mode 0, 1 or 2.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3380-L3386
                    time = data(:,1);
                    y = data(:,2);
                    
                    if clip_high == 1
                        if clip_set == 0
                            y(y<clip_value) = clip_value;
                            y = y - clip_value;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3388-L3390
                        elseif clip_set ==1
                            time(y<clip_value) = [];
                            y(y<clip_value) = [];
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3392-L3393
                        elseif clip_set ==2
                            y(y<clip_value) = clip_value;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3401-L3406
                        end
                        
                    else
                        if clip_set == 0
                            y(y>clip_value) = clip_value;
                            y = y - clip_value;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3408-L3410
                        elseif clip_set ==1
                            time(y>clip_value) = [];
                            y(y>clip_value) = [];
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3412-L3413
                        elseif clip_set ==2
                            y(y>clip_value) = clip_value;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3421-L3424
                        end
                    end

                        data1 = [time,y];
%% End copied source
r = struct();
r.data1 = data1;
end

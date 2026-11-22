function layout_metrics(fig,id,profile,folder)
% Read printable object extents from a reopened FIG, relative to its canvas.
drawnow;
fig.Units='pixels'; canvas=fig.Position(3:4);
report.figure=id; report.profile=profile; report.canvas_px=canvas;
axList=findall(fig,'Type','axes'); panels=cell(1,numel(axList));
objects={};
for k=1:numel(axList)
    ax=axList(k); px=getpixelposition(ax,true);
    panels{k}=struct('tag',ax.Tag,'box',normbox(px,canvas),'xlim',ax.XLim,...
        'ylim',ax.YLim,'xtick',ax.XTick,'xticklabel',{cellstr(string(ax.XTickLabel))},'visible',ax.Visible);
    for h=reshape(findall(ax,'Type','text'),1,[])
        txt=char(join(string(h.String),' ')); 
        if isempty(strtrim(txt)) || strcmp(h.Visible,'off'),continue,end
        role=h.Tag;
        if h==ax.XLabel,role='xlabel';elseif h==ax.YLabel,role='ylabel';elseif h==ax.Title,role='title';end
        if isempty(role),role='text';end
        units=h.Units; h.Units='pixels'; e=h.Extent; h.Units=units;
        if numel(e)~=4 || any(~isfinite(e)),continue,end
        e(1:2)=e(1:2)+px(1:2)-1;
        objects{end+1}=struct('role',role,'text',txt,'interpreter',h.Interpreter,'panel',k,'box',normbox(e,canvas)); %#ok<AGROW>
    end
end
for h=reshape(findall(fig,'Type','legend'),1,[])
    h.Units='normalized';
    objects{end+1}=struct('role','legend','text',char(join(string(h.String),' | ')), ...
        'interpreter',h.Interpreter,'panel',0,'box',h.Position); %#ok<AGROW>
end
for h=reshape(findall(fig,'Tag','band-note'),1,[])
    h.Units='normalized';
    objects{end+1}=struct('role','note','text',h.String,'interpreter',h.Interpreter,'panel',0,'box',h.Position); %#ok<AGROW>
end
report.axes=panels; report.objects=objects;
file=fopen(fullfile(folder,'layout.json'),'w'); cleanup=onCleanup(@()fclose(file));
fwrite(file,unicode2native(jsonencode(report),'UTF-8'),'uint8');
end
function result=normbox(rect,canvas)
result=(rect-[1 1 0 0])./[canvas canvas];
end

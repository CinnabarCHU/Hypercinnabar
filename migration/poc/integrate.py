"""Connect the code-only desktop to Core, retaining versioned controls and exports."""
from pathlib import Path
import re


def replace(s, old, new):
    if s.count(old) != 1:
        raise ValueError(f"Expected one pinned source anchor: {old[:95]!r}")
    return s.replace(old, new)


def section(s, start, stop, text):
    a = s.index(start)
    b = s.index(stop, a)
    return s[:a] + text + "\n" + s[b:]


def integrate(dest, tree):
    code = dest/"code"
    gui = code/"guicode"
    misc = code/"misc"
    if tree == "master":
        f = code/"package/bispectral/bispectralGUI.m"
        s = f.read_text()
        s = replace(s, "options.ProgressFcn = @updateProgress;\n            result = bispectralAnalyze(app.Data,options);",
                    "[candidateSession,result] = acgui.bispectral(app.Data,options,@updateProgress);")
        s = replace(s,"app.LastResult = result;","app.LastResult = result;\n            setappdata(app.UIFigure,'AcycleAnalysis',candidateSession);")
        f.write_text(s)
        return

    # Shared preference replaces the relative ac_pwd.txt in the scientific callbacks.
    for f in code.rglob("*.m"):
        raw = f.read_bytes()
        raw = raw.replace(b"fileread('ac_pwd.txt')", b"accore.io('workspace')")
        raw = raw.replace(b"which('ac_pwd.txt')", b"accore.io('workspaceFile')")
        f.write_bytes(raw)
    # Preserve real file-dialog and per-window selection behavior. Numeric reads
    # from files chosen in the main list go through the same I/O entry as the CLI.
    f = gui/"AC.m"
    s = f.read_text()
    s = section(s,"if exist('ac_pwd.txt', 'file') == 2","handles.sortdata", "cd(accore.io('workspace'));")
    s = re.sub(r"\bload\((data_name|plot_filter_s|handles\.plot_s\{\d+\})\)",
               r"accore.io('read',\1)",s)
    # Numerical transect sampling follows the coordinates collected by the original
    # data cursor. Preserve the image overlay windows and the three historical files.
    a = s.index("function menu_improfile_Callback")
    b = s.index("\nfunction ",a+10)
    profile = s[a:b]
    profile = replace(profile,"I = imread(data_name);","I = imread(data_name); originalImage = I;")
    profile = re.sub(r"(?m)^\s*\[[^\n]*\]\s*=\s*improfile\([^;\n]+;\n","",profile)
    profile = section(profile,"                            % pixels","                            name = [dat_name", """                            sample = accli.run('menu_improfile',struct('I',originalImage, ...
                                'CursorInfo_value',CursorInfo_value,'color_type',imfinfo1.ColorType));
                            setappdata(figI,'AcycleAnalysis',sample);
                            data = sample.res.data; czp = sample.res.czp;
                            xi = sample.res.xi; yi = sample.res.yi;""")
    s = s[:a] + profile + s[b:]
    f.write_text(s)
    (misc/"refreshcolor.m").write_text("acgui.refresh(handles,pwd);\n")
    # Preserve the original frequency prompts, range repair and output naming.
    f = gui/"ft.m"
    s = f.read_text()
    s = section(s,"data_s = varargin{1}.current_data;","handles.data_name =",
                """handles.bandpassSession = accli.run('menu_filter',varargin{1}.current_data);
data_s = handles.bandpassSession.params.data;
handles.current_data = data_s;""")
    s = section(s,"[po2,w2] = pmtm(","set(handles.edit10,", """po2 = handles.bandpassSession.dat.po2; fd2 = handles.bandpassSession.dat.fd2;
f = handles.bandpassSession.res.f; P1 = handles.bandpassSession.res.P1;
style = handles.bandpassSession.plt;
handles.x_1 = style.x_1; handles.x_2 = style.x_2; handles.y_1 = style.y_1;
handles.y_2 = style.y_2; handles.y_3 = style.y_3;""")
    f.write_text(s)
    f = misc/"update_filter_axes.m"
    s = f.read_text()
    s = section(s,"L = length(data(:,2));","handles.add_list = add_list;", """plotStyle = struct('x_1',x_1,'x_2',x_2,'y_1',y_1,'y_2',y_2,'unit',handles.unit);
if ismember(filter,{'Gaussian','Taner-Hilbert','Cheby1','Ellip','Butter'})
    science = struct('filter',filter,'flow',flch(1),'fhigh',flch(3),'taner_c',taner_c);
    handles = acgui.filterPreview(handles,science,plotStyle);
    data_filterout = handles.data_filterout;
    suffix = ['-flow-',num2str(flch(1)),'-fhigh-',num2str(flch(3))];
    label = filter;
    if strcmp(filter,'Gaussian'), label = 'Gau'; end
    if strcmp(filter,'Taner-Hilbert')
        label = 'Tan'; suffix = [suffix,'-e',num2str(log10(taner_c))];
        handles.filterdd = data_filterout;
        for part = {'AM','ufaze','ufazedet','ifaze','ifreq'}
            handles.(['add_list_',lower(part{1})]) = [handles.dat_name,'-Tan',suffix,'-',part{1},'.txt'];
        end
    end
    add_list = [handles.dat_name,'-',label,suffix,'.txt'];
    if strcmp(filter,'Taner-Hilbert'), set(handles.edit18,'enable','on');
    else, set(handles.edit18,'enable','off'); end
else
    add_list = ''; data_filterout = '';
    axes(handles.ft_axes3); plot(handles.bandpassSession.res.f,handles.bandpassSession.res.P1);
    xlim([x_1 x_2]); ylim([y_1 y_2]);
    xlim(handles.ft_axes4,[x_1 x_2]);
end""")
    f.write_text(s)
    # The alternative high/low/stop filter controls keep their native filenames.
    f = misc/"update_filter_axes4.m"
    s = f.read_text()
    s = section(s,"axes(handles.ft_axes3);","handles.add_list = add_list;", """if ismember(filter_s,{'Butter','Cheby1','Ellip'})
    science = struct('passtype',passtype,'filter_s',filter_s,'f11',f11);
    if strcmp(passtype,'bandstopiir'), science.f12 = f12; end
    style = struct('x_1',x_1,'x_2',x_2,'y_1',y_1,'y_2',y_2);
    result = accli.run('menu_filter',struct('data',data),'Operation','PassFilter_legacy', ...
        'Params',science,'Plt',style,'Target',handles.ft_axes3);
    setappdata(ancestor(handles.ft_axes3,'figure'),'AcycleAnalysis',result);
    xlim(handles.ft_axes4,[x_1,x_2]);
    limits = num2str(f11);
    if strcmp(passtype,'bandstopiir'), limits = [num2str(min(f11,f12)),'-',num2str(max(f11,f12))]; end
    handles.filename = handles.dat_name;
    add_list = [handles.filename,passtype,lower(filter_s),'-',limits,'.txt'];
    data_filterout = result.res.data_filterout;
else
    add_list = ''; data_filterout = [];
end""")
    f.write_text(s)
    # Multiselect overlays and the export-column ordering stay in the old desktop.
    # Each trend is computed through the registered analyzer and persists separately.
    f = gui/"prewhiten.m"
    s = f.read_text()
    s = replace(s,"handles.prewhiten_emdres = 'noteemdres';\n% Update",
                "handles.prewhiten_emdres = 'noteemdres';\nupdate_detrend_plot_fig\n% Update")
    f.write_text(s)
    f = misc/"update_detrend_plot_fig.m"
    s = f.read_text()
    s = replace(s,"plot(datax,datay,'-k');", """[handles,rawResult] = acgui.trend(handles,'raw',3,smooth_win);
ax = get(handles.detrendfig,'CurrentAxes');
if isempty(ax), ax = axes('Parent',handles.detrendfig); end
handles.trendSessions.raw = accli.replot(handles.trendSessions.raw,struct(),ax);
setappdata(handles.output,'AcycleAnalysis',handles.trendSessions.raw);
axes(ax)""")
    for start, stop, key, var, degree in [
        ("    datamean = dataymean * ones(npts,1);","    hlin =","mean","datamean","3"),
        ("    sdat=polyfit(datax,datay,1);","    plot(datax,datalinear","linear","datalinear","3"),
        ("    sdat=polyfit(datax,datay,2);","    plot(datax,data2nd","quadratic","data2nd","3"),
        ("    sdat=polyfit(datax,datay,polynomial_value);","    plot(datax,datamore","polynomial","datamore","polynomial_value"),
        ("    [imfs,~,~] = emd(datay);","    figure(fig)","eemd","dataEMDres","3")]:
        s = section(s,start,stop,f"    [handles,fit] = acgui.trend(handles,'{key}',{degree},smooth_win); {var} = fit.trend;")
    for key in ("lowess","rlowess","loess","rloess"):
        s = replace(s,f"data{key}=smooth(datax,datay, smooth_win,'{key}');",
                    f"[handles,fit] = acgui.trend(handles,'{key}',3,smooth_win); data{key} = fit.trend;")
    f.write_text(s)
    # Preserve SWA's choices, automatic confidence flags and historical three files.
    f = gui/"SWAgui.m"
    s = f.read_text().replace("global freq","% Frequency belongs to this window.")
    s = section(s,"[freq, power, swa, alphob","set(edit1,'String'", """session = accli.run('menu_swa',struct('data_r',data_r,'filename',handles.data_name,'unit',handles.unit));
freq = session.res.freq; power = session.res.power; swa = session.res.swa;
clfdr = session.res.clfdr; chi2_inv_value = session.res.chi2_inv_value;
setappdata(f,'AcycleAnalysis',session);
""")
    s = replace(s,"movefile('SWA-Periodogram-Bayes-prob.dat', [fName,'-SWA-Periodogram-Bayes-prob-',date,'.dat']);",
                "accore.io('writeText',[fName,'-SWA-Periodogram-Bayes-prob-',date,'.dat'],session.res.reports.probabilities);")
    s = replace(s,"movefile('SWA-Spectrum-background-FDR.dat',[fName,'-SWA-Spectrum-FDR-',date,'.dat']);",
                "accore.io('writeText',[fName,'-SWA-Spectrum-FDR-',date,'.dat'],session.res.reports.spectrum);")
    s = section(s,"    % Define refreshSWAfigure","%% how many figures", """    style = struct('curves',logical([checkbox1x.Value]),'figure_count',find([checkbox3x.Value],1), ...
        'log_y',logical(checkbox22.Value),'log_x',logical(checkbox23.Value),'period_axis',logical(checkbox24.Value), ...
        'fmin',str2double(edit1.String),'fmax',str2double(edit2.String));
    session = accli.replot(session,style);
    setappdata(f,'AcycleAnalysis',session);
end""")
    # Old script opened the preference file for writing without closing it.
    s = section(s,"ac_pwd_str = ","refreshcolor;","")
    f.write_text(s)

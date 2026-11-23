# Ocean Drilling Program · Leg 138

Leg 138 于 1991 年在赤道东太平洋钻探 Sites 844–854。本分支按航前计划、航后初报、Initial Reports、Scientific Results 和随盘材料维护可校读的数字版本。原站号、孔号、图表号、发布版本、源行和页码都可以作为查询入口。

- [84 页现代校读本](Leg138/publication/ODP138_Leg_Report_Edition.pdf) 包含逐站阅读、原图与重绘对照、岩芯取色示范和出版差异的校记。
- [使用与复建说明](Leg138/README.md) 列出离线浏览、全文检索、API、按出处导出以及复核方式。
- [分发件的校验记录](Leg138/data/source_package_checks.json) 登记 5,425 项原件。底本可从原分发站按需拉取，在本地按已登记的哈希核对。
- [ODP 官方卷目录](https://www-odp.tamu.edu/publications/138_IR/main.htm) 与 [Scientific Results](https://www-odp.tamu.edu/publications/138_SR/main.htm) 提供原始出版信息。引用数据时请连同对象所列的章节、表和发布版本引用原作者。

```sh
git clone --single-branch --branch odp-leg138 https://github.com/CinnabarCHU/Hypercinnabar.git
cd Hypercinnabar/Leg138
python tools/build_catalog.py
python tools/verify_catalog.py
python tools/serve.py
```

服务入口为 <http://127.0.0.1:8138/>。无需 Python 服务也可直接用浏览器打开解压或检出到本地的 `Leg138/browse.html`，按站浏览和导出。原出版物和数据保留来源、署名与原有权利说明。

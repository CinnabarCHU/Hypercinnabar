GUIDE 旧版（`RGBToGray_legacy`）的参数准备、计算与绘图均已完成，输出与当前版完全一致。

## 旧版运行记录

| 阶段 | run_id | 状态 |
|---|---|---|
| 参数准备 (helper) | `20261123T120900Z-6fda234c2a6c` | completed |
| 数值计算 (analyzer) | `20261123T121101Z-a22d5eb98355` | completed |
| 绘图 (plotter) | `20261123T121257Z-60b2e2bb99c2` | completed |

输入仍是同一附件（SHA-256 `ab58defa…5cf4`，3×2 像素 RGB），`params.im_name` 为 2×3×3 `uint8`，`params.operation = "RGBToGray_legacy"`（revision = guide，pin `74082d52`，与当前版同一仓库版本）。

## 旧版输出矩阵

`I = uint8([76 150 29; 0 255 128])`（2×3 `uint8`）

## 当前版 vs GUIDE 旧版 逐一对比

| 行 \ 列 | 当前版 `RGBToGray`<br>`20261123T120137Z-d22f016503d9` | GUIDE 旧版 `RGBToGray_legacy`<br>`20261123T121101Z-a22d5eb98355` | 差值 |
|---|---|---|---|
| (1,1) | 76 | 76 | 0 |
| (1,2) | 150 | 150 | 0 |
| (1,3) | 29 | 29 | 0 |
| (2,1) | 0 | 0 | 0 |
| (2,2) | 255 | 255 | 0 |
| (2,3) | 128 | 128 | 0 |

**结论：两版本输出矩阵完全相同**——6/6 元素差值为 0，数据类型均为 `uint8`，尺寸均为 2×3。旧版对应的原始像素映射也一致：红→76、绿→150、蓝→29、黑→0、白→255、中灰→128，即两版都采用同一组 BT.601 亮度权重（0.2989/0.5870/0.1140）并做相同的取整。这一行为符合预期：GUIDE 旧版与当前版在该菜单中是同一转换核心的不同 GUI 封装，算法未变。

## 旧版绘图

![20261123T121257Z-60b2e2bb99c2: figure_01](<../runs/20261123T121257Z-60b2e2bb99c2/figure_01.png>)

Acycle 原始 MATLAB 绘图（`RGBToGray_legacy`，plotter `20261123T121257Z-60b2e2bb99c2`）：以 `imshow` 显示 2×3 灰度结果。因源图仅 3×2 像素，成图仅 10×9 像素，只能看出整体明暗分布（左下最暗 = 0，中下最亮 = 255）。该 PNG 与当前版 figure 的像素内容一致（规范化预览的 sha256 同为 `47151ad6…d4544`），说明两版绘图路径也给出相同的栅格结果。

## 说明与限制

- 源图 81 字节、3×2 像素，是标准色块测试图，因此"完整矩阵"只有 6 个值；结论可覆盖的仅是这一极小输入，不能据此外推两版在抗锯齿、索引色/16 位 PNG、EXIF 方向等复杂输入上的等价性——这些情形本次未测试。
- 我读取了两张 MATLAB 生成的 PNG 做视觉复核，但 10×9 像素的图无法逐点核对；等价性判定以 MATLAB 输出矩阵为准（已用 BT.601 权重独立重算验证）。
- 绘图与记录均为新增，未覆盖任何既有结果。

## 全部运行记录（均已保留）

| run_id | 操作 | 角色 | 状态 |
|---|---|---|---|
| `20261123T115727Z-7f4853b8b4c1` | `RGBToGray` | helper | completed |
| `20261123T120137Z-d22f016503d9` | `RGBToGray` | analyzer | completed |
| `20261123T120354Z-7269282e94e2` | `RGBToGray` | plotter | completed |
| `20261123T120620Z-97b928c26dc6` | `RGBToGray` | replay | completed |
| `20261123T120900Z-6fda234c2a6c` | `RGBToGray_legacy` | helper | completed |
| `20261123T121101Z-a22d5eb98355` | `RGBToGray_legacy` | analyzer | completed |
| `20261123T121257Z-60b2e2bb99c2` | `RGBToGray_legacy` | plotter | completed |

下载：[旧版 figure_01.png](<../runs/20261123T121257Z-60b2e2bb99c2/figure_01.png>)、[旧版 journal_zip](<../runs/20261123T121257Z-60b2e2bb99c2/acycle-journal.zip>)、[当前版 journal_zip](<../runs/20261123T120137Z-d22f016503d9/acycle-journal.zip>)。

/** Known RGB primaries exercise typed MATLAB results through the installed DSH tool executor. */
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

export async function verifyMenuScience(call, workspace) {
  const menu = 'menu_rgb2gray'
  const bytes = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAMAAAACCAIAAAASFvFNAAAAGElEQVR4nAXBAQEAAAjDIIz+5BOE0KHa9j7oB3+xZADCAAAAAElFTkSuQmCC', 'base64')
  const digest = createHash('sha256').update(bytes).digest('hex')
  const runs = []
  for (const operation of ['RGBToGray', 'RGBToGray_legacy']) {
    const input_path = operation + '.png'
    await writeFile(join(workspace, input_path), bytes)
    const h = await call('acycle_menu_helper', { menu, input: { operation }, input_kind: 'image', input_path })
    assert.equal(h.input_sha256, digest)
    assert.equal(h.selector, operation)
    await writeFile(join(workspace, input_path), 'changed after preparation')
    const a = await call('acycle_menu_analyzer', { menu, helper_run_id: h.run_id })
    assert.equal(a.completion, 'done')
    assert.equal(a.summary.preview.I.class, 'uint8')
    assert.deepEqual(a.summary.preview.I.value, [[76, 150, 29], [0, 255, 128]])
    const replay = await call('acycle_menu_replay', { run_id: a.run_id })
    assert.deepEqual(replay.summary, a.summary)
    assert.notEqual(replay.run_id, a.run_id)
    const p = await call('acycle_menu_plotter', { menu, helper_run_id: h.run_id, analyzer_run_id: a.run_id, target: 'axes' })
    assert.equal(p.completion, 'done')
    const png = await readFile(p.artifacts.figure_01)
    assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a')
    assert.equal((await readFile(a.artifacts.journal_zip)).subarray(0, 2).toString(), 'PK')
    runs.push({ operation, helper: h.run_id, analyzer: a.run_id, plotter: p.run_id, replay: replay.run_id })
  }
  const series = 'series.csv'
  await writeFile(join(workspace, series), '0,0\n2,4\n4,8\n')
  const prep = await call('acycle_menu_helper', { menu: 'menu_interp', input_path: series,
    input: { operation: 'RegularInterpolation', samplingInterval: 1 } })
  const interpolated = await call('acycle_menu_analyzer', { menu: 'menu_interp', helper_run_id: prep.run_id })
  assert.deepEqual(interpolated.summary.preview.interpolated.value, [[0,0],[1,2],[2,4],[3,6],[4,8]])
  runs.push({ operation: 'RegularInterpolation', helper: prep.run_id, analyzer: interpolated.run_id })
  const failure = await call('acycle_menu_analyzer', { menu, params: { operation: 'RGBToGray' } }, true)
  const id = JSON.stringify(failure).match(/\d{8}T\d{6}Z-[0-9a-f]{12}/)?.[0]
  assert.ok(id, JSON.stringify(failure))
  const record = await call('acycle_get_run', { run_id: id })
  assert.equal(record.status, 'failed')
  assert.equal(record.completion, 'cancelled')
  assert.ok(record.journal)
  console.log(JSON.stringify({ verified_menu_science: runs, missing_required_input: id }))
}

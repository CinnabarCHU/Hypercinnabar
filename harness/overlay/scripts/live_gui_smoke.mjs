import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { join } from 'node:path'
import { writeFile } from 'node:fs/promises'

export async function verifyLiveGui(call, workspace) {
  const testRoot = join(process.env.GITHUB_WORKSPACE, 'tests')
  const human = action => execFileSync('python', [join(testRoot, 'gui_human.py'), action], { stdio: 'inherit' })
  const capture = (title, name) => execFileSync('python', [join(testRoot, 'capture_acycle_window.py')], {
    stdio: 'inherit', env: { ...process.env, ACYCLE_CAPTURE_TITLE: title, ACYCLE_CAPTURE_PNG: join(process.env.RUNNER_TEMP, name) }
  })
  const evidence = []
  async function invoke(name, args) {
    const res = await call('acycle_gui_' + name, args)
    evidence.push({ name, arguments: args, result: res })
    await writeFile(join(process.env.RUNNER_TEMP,'gui-receipts.json'),JSON.stringify(evidence,null,2))
    return res
  }
  const { windows } = await invoke('inspect', {})
  assert.equal(windows.length, 1)
  let f = windows[0]
  assert.equal(f.operation, 'Bandpass_legacy')
  const id = f.window_id
  const update = (rev, values) => invoke('update', { window_id: id, expected_revision: rev, ...values })
  const firstAnalyzer = f.analysis_ids.analyzer
  f = await update(f.revision, { params: { flow: .04, fhigh: .06 } })
  assert.equal(f.window_id, id); assert.equal(f.params.flow, .04); assert.equal(f.params.fhigh, .06)
  assert.notEqual(f.analysis_ids.analyzer, firstAnalyzer)
  const recalculated = f.analysis_ids.analyzer
  const lastPlot = f.analysis_ids.plotter
  f = await update(f.revision, { plt: { x_2: .17 } })
  assert.equal(f.analysis_ids.analyzer, recalculated); assert.notEqual(f.analysis_ids.plotter, lastPlot)
  assert.equal(f.plt.x_2, .17)
  human('verify_export'); human('capture_filter'); capture(f.title,'live-filter.png')
  const oldRevision = f.revision
  human('manual_edit')
  f = await invoke('inspect', { window_id: id })
  assert.equal(f.params.fhigh, .065); assert.ok(f.revision > oldRevision)
  const conflict = await update(oldRevision, { params: { fhigh: .075 } })
  assert.equal(conflict.status, 'conflict'); assert.equal(conflict.current.revision, f.revision)
  const invalid = await update(f.revision, { params: { fhigh: .01 } })
  assert.equal(invalid.status, 'invalid'); assert.equal(invalid.current.analysis_ids.analyzer, f.analysis_ids.analyzer)
  assert.equal(invalid.current.revision, f.revision)
  human('save_exchange')
  const original = f
  let response = await invoke('open', { feature:'filter', input_path:'second.csv' })
  assert.equal(response.status,'conflict')
  response = await invoke('open', { feature:'filter', input_path:'second.csv', window_id:id, expected_revision:f.revision })
  assert.equal(response.window_id,id); assert.ok(response.revision>f.revision); assert.match(response.input_path,/second\.csv$/)
  human('close_filter')
  assert.equal((await invoke('inspect',{window_id:id})).status,'closed')
  assert.equal((await update(response.revision,{params:{flow:.035}})).status,'closed')
  assert.equal((await invoke('open',{feature:'filter',input_path:'series.csv',window_id:id,expected_revision:response.revision})).status,'closed')
  f = await invoke('open',{feature:'filter',input_path:'filter-exchange.mat'})
  assert.notEqual(f.window_id,id); assert.equal(f.analysis_ids.analyzer,original.analysis_ids.analyzer)
  assert.equal(f.params.fhigh,.065); assert.equal(f.plt.x_2,.17)
  const cursor = (await invoke('inspect',{})).cursor
  let img = await invoke('open',{feature:'image_profile',input_path:'core.png'})
  assert.equal(img.status,'awaiting_input')
  human('first_image_point')
  img = await invoke('inspect',{window_id:img.window_id})
  assert.equal(img.status,'awaiting_input'); assert.deepEqual(img.points,[[2,3]])
  human('finish_image')
  img = await invoke('inspect',{window_id:img.window_id})
  assert.equal(img.status,'completed'); assert.deepEqual(img.points,[[2,3],[9,7]])
  let stream = await invoke('events',{window_id:img.window_id,after:cursor})
  const finished = stream.events.find(e=>e.kind==='completed')
  assert.deepEqual(finished.detail.points,img.points); assert.equal(finished.detail.analyzer_id,img.analysis_ids.analyzer)
  capture(img.title,'live-image-profile.png'); human('close_images')
  const next = await invoke('open',{feature:'image_profile',input_path:'core.png'})
  execFileSync('python',[join(testRoot,'capture_acycle_window.py'),'--click-center'],{
    stdio:'inherit',env:{...process.env,ACYCLE_CAPTURE_TITLE:next.title}
  })
  let picked
  for (let attempt=0; attempt<10; attempt++) {
    picked = await invoke('inspect',{window_id:next.window_id})
    if (picked.points.length) break
    await new Promise(resolve => setTimeout(resolve,150))
  }
  assert.equal(picked.points.length,1)
  assert.ok(picked.points[0].length===2 && picked.points[0].every(v=>v>=1 && v<=10))
  human('close_images')
  stream = await invoke('events',{window_id:next.window_id,after:stream.cursor})
  assert.ok(stream.events.some(e=>e.kind==='cancelled'))
  console.log('PASS GUI attach, rerun, restyle, exported numbers, manual edit, stale/invalid edits, rebind, close, MAT reopen, native image picks, X11 pointer input and cancellation')
}

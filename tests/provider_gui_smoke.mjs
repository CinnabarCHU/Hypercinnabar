// Optional test transport. Only the two specified frequencies and axis limit
// on this exact synthetic window are accepted. No provider credentials in CI.
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { rename, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { setTimeout as delay } from 'node:timers/promises'

export async function verifyProviderAction(call) {
  const root = process.env.RUNNER_TEMP
  const repo = process.env.GITHUB_WORKSPACE
  const run = process.env.GITHUB_RUN_ID
  const state = await call('acycle_gui_inspect', {})
  assert.equal(state.windows.length, 1)
  const before = state.windows[0]
  const snapshot = join(root, 'provider-window.json')
  await writeFile(snapshot + '.tmp', JSON.stringify(state))
  await rename(snapshot + '.tmp', snapshot)

  const git = args => execFileSync('git', args, { cwd: repo, stdio: ['ignore', 'pipe', 'pipe'], encoding: 'utf8', timeout: 20_000 })
  const until = Date.now() + 420_000
  let received
  while (Date.now() < until) {
    try {
      git(['fetch', '--quiet', '--depth=1', 'origin', 'refs/heads/acycle-harness-gui-poc'])
      const data = JSON.parse(git(['show', 'FETCH_HEAD:tests/evidence/gui-model-action.json']))
      if (data.run === run) { received = data.call; break }
    } catch {}
    await delay(4000)
  }
  assert.ok(received, 'No model response for the active synthetic window.')
  assert.equal(received.name, 'acycle_gui_update')
  assert.deepEqual(received.arguments, {
    window_id: before.window_id, expected_revision: before.revision,
    params: { flow: .035, fhigh: .055 }, plt: { x_2: .13 }
  })
  const result = await call(received.name, received.arguments)
  assert.equal(result.window_id, before.window_id)
  assert.ok(result.revision > before.revision)
  assert.equal(result.params.flow, .035)
  assert.equal(result.params.fhigh, .055)
  assert.equal(result.plt.x_2, .13)
  assert.equal(result.unit,'m'); assert.equal(result.frequency_unit,'cycles/m')
  assert.notEqual(result.analysis_ids.analyzer, before.analysis_ids.analyzer)
  execFileSync('python', [join(repo, 'tests/gui_human.py'), 'verify_export'], { stdio: 'inherit' })
  const after = await call('acycle_gui_inspect', {window_id: before.window_id})
  assert.deepEqual(after, result)
  await writeFile(join(root, 'provider-update.json'), JSON.stringify({before, call: received, result, after}, null, 2))
  console.log('PASS external model command in the same shared desktop, with numeric export verification')
}

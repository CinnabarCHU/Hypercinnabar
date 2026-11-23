// The only outbound payload is the explicit snapshot of this synthetic test window.
const { DefaultArtifactClient } = require(process.env.RUNNER_TEMP + '/fixture-publisher/node_modules/@actions/artifact')
const fs = require('node:fs/promises')
const path = require('node:path')
const { setTimeout: delay } = require('node:timers/promises')
async function publish() {
  const dir = process.env.RUNNER_TEMP
  const file = path.join(dir, 'provider-window.json')
  const deadline = Date.now() + 600_000
  for (;;) {
    try { await fs.access(file); break } catch (err) { if (err.code !== 'ENOENT') throw err }
    if (Date.now() > deadline) throw Error('No synthetic window snapshot.')
    await delay(1000)
  }
  const artifact = new DefaultArtifactClient()
  const { id } = await artifact.uploadArtifact('GUI-provider-inspect', [file], dir, { retentionDays: 7 })
  console.log('Published the synthetic inspect response', id)
}
publish().catch(err => { console.error(err.message); process.exitCode = 1 })

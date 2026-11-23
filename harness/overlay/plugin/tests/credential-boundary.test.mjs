import assert from 'node:assert/strict'
import test from 'node:test'
import { mkdtemp, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { runBridge } from '../index.mjs'

test('provider credential never reaches the numerical child, even through overrides', async t => {
  const root = await mkdtemp(join(tmpdir(), 'acycle-credential-'))
  const before = process.env.DEEPSEEK_API_KEY
  t.after(async () => {
    if (before === undefined) delete process.env.DEEPSEEK_API_KEY
    else process.env.DEEPSEEK_API_KEY = before
    await rm(root, { recursive: true, force: true })
  })
  process.env.DEEPSEEK_API_KEY = 'test-only-provider-credential'
  const executable = join(root, 'worker')
  await writeFile(executable, '#!/usr/bin/env python3\nimport json,os\nprint(json.dumps({"has_credential":"DEEPSEEK_API_KEY" in os.environ,"workspace":os.environ.get("ACYCLE_WORKSPACE")}))\n', { mode: 0o700 })
  for (const extra of [{}, { DEEPSEEK_API_KEY: 'test-only-override' }]) {
    assert.deepEqual(await runBridge({}, { python: executable,
      environment: { ACYCLE_WORKSPACE: root, ...extra } }), { has_credential: false, workspace: root })
  }
  assert.equal(process.env.DEEPSEEK_API_KEY, 'test-only-provider-credential')
})

test('worker results and errors redact provider credentials', async t => {
  const root = await mkdtemp(join(tmpdir(), 'acycle-redaction-'))
  t.after(() => rm(root, { recursive: true, force: true }))
  const executable = join(root, 'worker')
  const environment = { DEEPSEEK_API_KEY: 'test-only-override' }
  await writeFile(executable, '#!/usr/bin/env python3\nimport json\nprint(json.dumps({"message":"test-only-override"}))\n', { mode: 0o700 })
  assert.deepEqual(await runBridge({}, { python: executable, environment }), { message: '[REDACTED]' })
  await writeFile(executable, '#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps({"status":"failed","error":"test-only-override"}));sys.exit(1)\n', { mode: 0o700 })
  await assert.rejects(runBridge({}, { python: executable, environment }), error => {
    assert.ok(error.message.includes('[REDACTED]'))
    assert.ok(!error.message.includes('test-only-override'))
    return true
  })
})

/** Native Cordis plugin. All tools share the Python transport -> MATLAB dispatcher. */
import { spawn } from 'node:child_process'
import { readFile, readdir } from 'node:fs/promises'
import { resolve, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { attachOutputs, deliveryConfig, importAttachment, renderResult, resolveInputAttachment } from './attachments.mjs'

export const name = 'acycle-matlab'
export const inject = ['tools', 'skills', 'workingDirectory', 'systemPrompt']
const skillRoot = fileURLToPath(new URL('./skills/', import.meta.url))
const MAX_OUTPUT = 16 * 1024 * 1024
// Python's MATLAB supervisor may need 5 s to escalate its separate process group,
// then up to 10 s to reap it and persist interrupted-run evidence.
const TERMINATION_GRACE_MS = 20_000
const WORKFLOW_POLICY = `Acycle research workflow
For methods outside the high-level tools, discover exact pinned entrypoints with acycle_catalog and execute typed local MATLAB steps with acycle_native. Read the source help before selecting positional arguments. Prefer calculation cores over GUI actions. Native source/API coverage does not establish headless GUI parity or numerical validation. Import each native input attachment explicitly, then use its frozen workspace path. Preserve explicit units and scientific assumptions.
Use acycle_menu_catalog to find scientific menu roles. Its operation records document the wrappers; do not look up wrapper operation names in the separate acycle_catalog of native source files. If the user only requests discovery, stop after catalogue queries: helper creates a recorded MATLAB invocation. Select master or the _legacy GUIDE operation during acycle_menu_helper. Pass the helper run_id to acycle_menu_analyzer and both run IDs to acycle_menu_plotter. To reproduce a role use acycle_menu_replay with the saved run_id. A role marked incomplete has partial results. Desktop-only commands need the original window.
Use Acycle's original MATLAB implementation for its scientific quality assessment, numerical analysis, statistics, and plotting. Python may handle attachment bytes, checksums, file-format structure, transport, and functions Acycle does not implement; bridge scientific work back to MATLAB wherever possible. Do not replace available Acycle scientific QA or calculations with shell/Python statistics. The default MATLAB analysis pipeline already performs scientific QA; external numerical pre-analysis is unnecessary.
Choose methods from the user's research question, documented data meaning, and applicable Acycle skills. For sedimentation-rate, age, or orbital interpretations, verify the required coordinate units, geological age constraints, orbital targets, and scientifically reasonable search range. If required information is missing, ask the user a concise clarification and wait before starting scientific analysis. Never infer units, age, or a rate range from a filename, numerical magnitudes, or a sample count. Structural attachment import and byte preview can proceed while clarification is pending.
For conversational changes to a completed run, prefer acycle_rerun with the requested changes together in parameter_patch. Preserve the saved input, operation, method, and effective settings except for changes the user requested. Do not restart a generic analysis that silently changes the original method. Retrieve completed outputs for display instead of recalculating them.
If a scientific tool fails and returns a run_id, report that run_id and its diagnostic, and stop the failed analysis attempt. Do not repeatedly resubmit a failed scientific computation or switch to Python as a numerical substitute. Do not alter authentication or execute gh auth to repair an analysis backend; report the setup problem for the operator. A presentation failure does not undo completed MATLAB results: reopen the saved run to recover its files.
Deliver key MATLAB figures in the main Chat by including the exact PNG Markdown returned in presentation.display_markdown in the final answer, together with short captions and the run ID. Keep the returned original-file links for downloads; do not invent image URLs or present bare filesystem text as an embedded image.
The plugin's offloaded previews alone do not give the model image pixels. When the selected model declares image input and read_image is available, read the existing MATLAB PNG when a visual review is needed; check that the tool actually returned an image before claiming visual inspection. If image input is unavailable or reading fails, say that visual review was not completed and still deliver the figures and numerical results. Numerical verification, model visual review, and user-visible Chat display are separate checks. Preserve statistical limitations and warnings in the answer.`

/** No shell expansion; arguments and paths travel as JSON through stdin. */
export function runBridge(request, { python = process.env.ACYCLE_PYTHON || 'python3', signal,
                                     timeoutMs = 3_600_000, environment = {} } = {}) {
  return new Promise((fulfill, reject) => {
    if (signal?.aborted) return reject(new Error('Acycle call cancelled'))
    // The model provider owns this credential; numerical workers never need it.
    // Remove it after applying overrides so config cannot reintroduce it.
    const childEnvironment = { ...process.env, ...environment }
    const secrets = [...new Set([process.env.DEEPSEEK_API_KEY, environment.DEEPSEEK_API_KEY].filter(Boolean))]
    const redact = value => secrets.reduce((text, secret) => text.replaceAll(secret, '[REDACTED]'), value)
    delete childEnvironment.DEEPSEEK_API_KEY
    const child = spawn(python, ['-m', 'acycle_deepseek.harness_bridge'], {
      stdio: ['pipe', 'pipe', 'pipe'], shell: false, detached: process.platform !== 'win32',
      env: childEnvironment,
    })
    let stdout = '', stderr = '', failure, forceTimer
    const stop = (reason) => {
      if (failure) return
      failure = reason
      const kill = (kind) => {
        try {
          if (process.platform !== 'win32' && child.pid) process.kill(-child.pid, kind)
          else child.kill(kind)
        } catch { /* It may already have exited. */ }
      }
      kill('SIGTERM')
      forceTimer = setTimeout(() => kill('SIGKILL'), TERMINATION_GRACE_MS)
      forceTimer.unref()
    }
    const abort = () => stop(new Error('Acycle call cancelled'))
    const timeout = setTimeout(() => stop(new Error('Acycle bridge timed out')), timeoutMs)
    timeout.unref()
    signal?.addEventListener('abort', abort, { once: true })
    const clean = () => {
      clearTimeout(timeout); clearTimeout(forceTimer)
      signal?.removeEventListener('abort', abort)
    }
    child.stdout.on('data', data => {
      stdout += data.toString()
      if (stdout.length > MAX_OUTPUT) stop(new Error('Acycle bridge output limit exceeded'))
    })
    child.stderr.on('data', data => { if (stderr.length < 20000) stderr += data.toString() })
    child.on('error', error => { clean(); reject(error) })
    child.on('close', code => {
      clean()
      if (failure) return reject(failure)
      if (code !== 0) {
        let record
        try { record = JSON.parse(stdout) } catch { /* Interpreter/startup failures may only reach stderr. */ }
        const structuredFailure = record && typeof record === 'object' &&
          (record.status === 'failed' || record.error) ? JSON.stringify(record) : null
        const raw = structuredFailure ?? stderr.slice(-4000)
        const detail = redact(raw)
        return reject(new Error(`Acycle bridge exited ${code}: ${detail}`))
      }
      try { fulfill(JSON.parse(redact(stdout))) }
      catch { reject(new Error('Acycle bridge returned invalid JSON')) }
    })
    child.stdin.on('error', () => {})
    child.stdin.end(JSON.stringify(request))
  })
}

export async function loadSkills(root = skillRoot) {
  let entries
  try { entries = await readdir(root, { withFileTypes: true }) }
  catch (error) { if (error.code === 'ENOENT') return []; throw error }
  const skills = []
  for (const entry of entries.filter(e => e.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
    const path = join(root, entry.name, 'SKILL.md')
    const content = await readFile(path, 'utf8')
    const nameMatch = content.match(/^name:\s*["']?([a-z0-9-]+)["']?\s*$/m)
    const descriptionMatch = content.match(/^description:\s*(.+)$/m)
    if (!nameMatch || !descriptionMatch) throw new Error(`Missing skill metadata: ${path}`)
    const description = descriptionMatch[1].replace(/^['"]|['"]$/g, '')
    skills.push({ name: nameMatch[1], description, path, source: 'bundled', provider: name,
      invocation: { modelInvocable: true, userInvocable: true },
      resourceBase: { kind: 'directory', path: join(root, entry.name) },
      content: content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '') })
  }
  return skills
}

export async function apply(ctx, config = {}) {
  const python = config.python || process.env.ACYCLE_PYTHON || 'python3'
  const configuredWorkspace = config.workspace || process.env.ACYCLE_WORKSPACE
  // Desktop launch environments need not inherit the terminal's MATLAB paths.
  // Apply this preset's explicit paths to its child only, never to other agents.
  const environment = {}
  if (config.menuRoot) environment.ACYCLE_MENU_ROOT = resolve(config.menuRoot)
  if (config.acycleRoot) environment.ACYCLE_ROOT = resolve(config.acycleRoot)
  if (config.matlabExecutable) environment.MATLAB_EXECUTABLE = config.matlabExecutable
  if (config.backend) environment.ACYCLE_BACKEND = config.backend
  const options = { python, timeoutMs: config.timeoutMs || 3_600_000, environment }
  const delivery = deliveryConfig(config)
  ctx.systemPrompt.section({ name: 'acycle:research-workflow', order: 3200,
    text: WORKFLOW_POLICY, interpolate: false })
  const workspaceFor = async exec => resolve(configuredWorkspace || (exec.agent
    ? await ctx.workingDirectory.ensure(exec.agent, exec.signal) : process.cwd()))
  const schemas = await runBridge({ action: 'schemas' }, options)
  for (const schema of schemas) {
    const fn = schema.function
    ctx.tools.register({
      name: fn.name, description: fn.description, parameters: fn.parameters,
      output: { schema: { type: 'object', additionalProperties: true },
                render: renderResult },
      async execute(args, exec) {
        const workspace = await workspaceFor(exec)
        const input = await resolveInputAttachment(ctx, args, workspace, exec, delivery)
        let value = await runBridge({ action: 'call', name: fn.name, arguments: input.args,
                           workspace }, { ...options, signal: exec.signal })
        if (input.imported) value = { ...value, imported_attachment: input.imported }
        if (fn.name === 'acycle_capabilities') value = { ...value, harness: {
          attachment_import_available: Boolean(ctx.get('attachments') && ctx.get('sessionQuery') && exec.agent),
          image_delivery_available: Boolean(ctx.get('attachments')),
          user_image_previews_do_not_imply_model_vision: true,
        } }
        return attachOutputs(ctx, value, workspace, exec, delivery, run_id => runBridge({
          action: 'call', name: 'acycle_get_run', arguments: { run_id }, workspace,
        }, { ...options, signal: exec.signal }))
      },
    })
  }
  ctx.tools.register({
    name: 'acycle_import_attachment',
    description: 'Import a user-uploaded numeric text, MAT, Excel, or raster image file from this Harness conversation into the Acycle workspace without changing bytes. Omit attachment_id for the latest single upload; a unique official 8-digit short handle is also accepted. Multiple uploads or ambiguous short handles return choices. Use the returned input_path for high-level analysis or in acycle_native.inputs. Native multi-input jobs import each attachment explicitly.',
    parameters: { type: 'object', additionalProperties: false, properties: {
      attachment_id: { type: 'string', description: 'A full sha256 attachment ID or its unique official 8-digit hexadecimal handle from this Session, optionally prefixed sha256:. Omit for the latest single uploaded file.' },
    } },
    output: { schema: { type: 'object', additionalProperties: true }, render: renderResult },
    async execute(args, exec) {
      return importAttachment(ctx, args, await workspaceFor(exec), exec, delivery)
    },
  })
  const skills = await loadSkills()
  const byName = new Map(skills.map(skill => [skill.name, skill]))
  ctx.skills.registerProvider(() => ({
    name,
    list: async () => skills.map(({ content, ...skill }) => ({ ...skill, rank: 600, locator: skill.name })),
    get: async candidate => byName.get(candidate.name),
  }))
}

/** Check the packaged plugin against the published official Cordis/tool/skill registries. */
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { resolve, join } from 'node:path'
import { readFile } from 'node:fs/promises'
const runtimeRoot = resolve(process.argv[2] || '/workspace/harness-runtime-smoke')
const workspace = resolve(process.argv[3] || '.')
const pluginPath = resolve(process.argv[4] || join(workspace, 'plugin/index.mjs'))
const require = createRequire(join(runtimeRoot, 'package.json'))
const load = async name => import(pathToFileURL(require.resolve(name)).href)
const { Context, Service } = await load('@deepseek-ai/cordis')
const { default: ToolRuntime } = await load('@deepseek-ai/dsh-tools')
const { default: SystemPrompt } = await load('@deepseek-ai/dsh-system-prompt')
const { default: SkillRegistry } = await load('@deepseek-ai/dsh-skill')
const version = JSON.parse(await readFile(require.resolve('@deepseek-ai/dsh-tools/package.json'), 'utf8')).version
const batched = version !== '0.2.1-rc.3'
const plugin = await import(pathToFileURL(pluginPath).href)
class WorkingDirectoryFixture extends Service {
  constructor(ctx) { super(ctx, 'workingDirectory') }
  async ensure() { return workspace }
}
const ctx = new Context()
try {
  await ctx.plugin(SystemPrompt)
  if (batched) {
    await ctx.plugin(ToolRuntime)
    const NativeExecutor = await load('@deepseek-ai/dsh-tool-executor-native')
    await ctx.plugin(NativeExecutor)
  } else {
    await ctx.plugin(ToolRuntime, { mode: 'native' })
  }
  await ctx.plugin(SkillRegistry)
  await ctx.plugin(WorkingDirectoryFixture)
  const live = process.argv.includes('--gui-live')
  const fiber = await ctx.plugin(plugin, { workspace, ...(live ? { guiEngine: 'AcycleDesktopTest' } : {}) })
  const tools = ctx.tools.schemas()
  assert.equal(tools.length, live ? 24 : 20)
  const skills = await ctx.skills.list()
  assert.equal(skills.length, 10)
  for (const skill of skills) assert.ok((await ctx.skills.get(skill.name)).content.length > 100)
  let sequence = 0
  async function call(name, args, shouldFail = false) {
    const id = 'acycle-smoke-' + (++sequence)
    const signal = new AbortController().signal
    const outcome = batched
      ? (await ctx.tools.execute({ calls: [{ type: 'tool-call', id, name, arguments: JSON.stringify(args) }], signal })).results[0].result
      : await ctx.tools.execute({ callId: id, name, arguments: args, signal })
    assert.equal(outcome.isError, shouldFail, JSON.stringify(outcome))
    return shouldFail ? outcome : outcome.value
  }
  const capabilities = await call('acycle_capabilities', {})
  assert.equal(capabilities.python_numerical_fallback, false)
  const catalogue = await call('acycle_menu_catalog', { menu: 'menu_rgb2gray' })
  assert.ok(catalogue.operations.includes('RGBToGray_legacy'))
  if (process.argv.includes('--menu-matlab')) {
    const { verifyMenuScience } = await import('./menu_science_smoke.mjs')
    await verifyMenuScience(call, workspace)
  }
  if (live) {
    const { verifyLiveGui } = await import('./live_gui_smoke.mjs')
    await verifyLiveGui(call, workspace)
  }
  await fiber.dispose()
  assert.equal(ctx.tools.schemas().length, 0)
  assert.equal((await ctx.skills.list()).length, 0)
  console.log(JSON.stringify({ status: 'passed', dsh_tools_version: version, plugin_path: pluginPath,
    registered_tools: tools.map(x => x.name), registered_skills: skills.map(x => x.name),
    capabilities, disposal: 'passed',
    scope: 'Official Cordis, tools and skills registries with fixed workspace fixture; not a full GUI session.' }, null, 2))
} finally { await ctx.fiber.dispose() }

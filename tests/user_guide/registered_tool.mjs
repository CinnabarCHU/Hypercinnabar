/** Invoke one user-visible tool via the pinned official DSH native executor. */
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { join, resolve } from 'node:path'
import { readFile, writeFile } from 'node:fs/promises'
const [job, result] = process.argv.slice(2)
const ws = resolve(process.env.ACYCLE_WORKSPACE)
const require = createRequire(join(resolve(process.env.ACYCLE_HARNESS_RUNTIME), 'package.json'))
const load = name => import(pathToFileURL(require.resolve(name)).href)
const { Context, Service } = await load('@deepseek-ai/cordis')
class Workspace extends Service { constructor(ctx) { super(ctx,'workingDirectory') } async ensure() { return ws } }
const ctx=new Context()
try {
  for (const n of ['@deepseek-ai/dsh-system-prompt','@deepseek-ai/dsh-tools','@deepseek-ai/dsh-tool-executor-native','@deepseek-ai/dsh-skill'])
    { const mod=await load(n); await ctx.plugin(mod.default ?? mod) }
  await ctx.plugin(Workspace)
  await ctx.plugin(await load('dsh-acycle'),{workspace:ws})
  const call=JSON.parse(await readFile(job,'utf8'))
  if(!ctx.tools.schemas().some(s=>s.name===call.name))throw Error('Tool not registered: '+call.name)
  const {results}=await ctx.tools.execute({calls:[{type:'tool-call',id:'guide',name:call.name,arguments:JSON.stringify(call.arguments)}],signal:new AbortController().signal})
  const outcome=results[0].result
  await writeFile(result,JSON.stringify(outcome.isError?outcome:outcome.value)+'\n')
  if(outcome.isError)process.exitCode=1
} finally {await ctx.fiber.dispose()}

// Invoke the installed native plugin through the official Cordis tool executor.
import assert from 'node:assert/strict'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {fileURLToPath,pathToFileURL} from 'node:url'
import {readFile,writeFile} from 'node:fs/promises'

const root = dirname(fileURLToPath(import.meta.url))
const runtime = join(root,'.test-env/harness')
const require = createRequire(join(runtime,'package.json'))
const load = async name => import(pathToFileURL(require.resolve(name)).href)
const config = JSON.parse(await readFile(process.argv[2],'utf8'))
const action = process.argv[3]
const {Context,Service} = await load('@deepseek-ai/cordis')
const {default:Tools} = await load('@deepseek-ai/dsh-tools')
const {default:SystemPrompt} = await load('@deepseek-ai/dsh-system-prompt')
const {default:Skills} = await load('@deepseek-ai/dsh-skill')
const Executor = await load('@deepseek-ai/dsh-tool-executor-native')
const plugin = await load('dsh-acycle')
class Workspace extends Service {
  constructor(ctx) { super(ctx,'workingDirectory') }
  async ensure() { return config.config.workspace }
}
const ctx = new Context()
const receipts = []
async function call(name,args) {
  const outcome = await ctx.tools.execute({calls:[{type:'tool-call',id:'local-'+(receipts.length+1),
    name,arguments:JSON.stringify(args)}],signal:new AbortController().signal})
  const result = outcome.results[0].result
  assert.equal(result.isError,false,JSON.stringify(result))
  receipts.push({name,arguments:args,result:result.value})
  return result.value
}
try {
  await ctx.plugin(SystemPrompt)
  await ctx.plugin(Tools)
  await ctx.plugin(Executor)
  await ctx.plugin(Skills)
  await ctx.plugin(Workspace)
  await ctx.plugin(plugin,config.config)
  assert.equal(ctx.tools.schemas().length,24)
  let result
  if (action === 'image') {
    result = await call('acycle_gui_open',{feature:'image_profile',input_path:'core.png'})
  } else if (action === 'events') {
    result = await call('acycle_gui_events',{})
  } else {
    result = await call('acycle_gui_inspect',{})
    const expected = resolve(config.config.workspace,'series.csv')
    const filter = result.windows.find(w=>w.feature==='filter' && resolve(w.input_path)===expected)
    assert.ok(filter,'Open the bundled series.csv using start_local_demo in MATLAB.')
    assert.equal(filter.operation,'Bandpass_legacy')
    assert.equal(filter.frequency_unit,'cycles/m')
    if (action === 'filter') {
      const updated = await call('acycle_gui_update',{window_id:filter.window_id,expected_revision:filter.revision,
        params:{flow:.035,fhigh:.055},plt:{x_2:.13}})
      assert.equal(updated.status,'ready')
      assert.equal(updated.window_id,filter.window_id)
      assert.equal(updated.params.flow,.035)
      assert.equal(updated.params.fhigh,.055)
      assert.equal(updated.plt.x_2,.13)
      result = await call('acycle_gui_inspect',{window_id:filter.window_id})
      assert.deepEqual(result,updated)
    }
  }
  const file = join(root,'generated','local-'+action+'.json')
  await writeFile(file,JSON.stringify({status:'passed',action,tools:24,receipts},null,2)+'\n')
  console.log(JSON.stringify(result,null,2))
  console.log('PASS '+action+' through the installed official Harness executor. Receipt saved to '+file)
} finally {
  await ctx.fiber.dispose()
}

// ecosystem.config.js
// PM2 process configuration for Averion
// Supports LOOP_MODE=asyncio (default) and LOOP_MODE=workers

const LOOP_MODE = process.env.LOOP_MODE || 'asyncio'

let apps = [
  {
    name: 'averion-api',
    script: 'api.py',
    interpreter: 'python3',
    watch: false,
    env: { NODE_ENV: 'production' }
  }
]

if (LOOP_MODE === 'asyncio') {
  // Default: single process handles all exchanges
  apps.push({
    name: 'averion-live',
    script: 'live_loop.py',
    interpreter: 'python3',
    watch: false,
    max_memory_restart: '1G'
  })
  apps.push({
    name: 'averion-research',
    script: 'research_loop.py',
    interpreter: 'python3',
    watch: false,
    max_memory_restart: '2G'
  })
} else {
  // LOOP_MODE=workers: separate process per exchange
  const exchanges = ['binance', 'mexc', 'kucoin', 'okx', 'bybit', 'gate', 'bitget']
  
  for (const ex of exchanges) {
    apps.push({
      name: `live-${ex}`,
      script: 'live_loop.py',
      interpreter: 'python3',
      watch: false,
      env: { EXCHANGE: ex },
      max_memory_restart: '512M'
    })
    apps.push({
      name: `research-${ex}`,
      script: 'research_loop.py',
      interpreter: 'python3',
      watch: false,
      env: { EXCHANGE: ex },
      max_memory_restart: '1G'
    })
  }
}

module.exports = { apps }

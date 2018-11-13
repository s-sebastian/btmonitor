module.exports = {
  devServer: {
    //proxy: {
    //  '/api': {
    //    target: 'http://lab.myshell.co.uk',
    //    changeOrigin: true,
    //  },
    //},
    allowedHosts: [
      'localhost',
    ],
    headers: {
      'Cache-Control': 'max-age=0, no-cache, no-store, must-revalidate',
      'Access-Control-Allow-Origin': '*'
    },
  },
  //baseUrl: '/',
  lintOnSave: false,
  runtimeCompiler: true,
  configureWebpack: {
    performance: {
      hints: false,
    },
  },
}

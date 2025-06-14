const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.js',
    videosFolder: 'cypress/videos',
    screenshotsFolder: 'cypress/screenshots',
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    env: {
      apiUrl: 'http://localhost:8080/api',
      coverage: true
    },
    setupNodeEvents(on, config) {
      // Code coverage setup
      require('@cypress/code-coverage/task')(on, config);
      
      // Custom tasks for testing
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },
        clearDatabase() {
          // Task to clear test database
          return null;
        },
        seedDatabase(data) {
          // Task to seed test database
          return null;
        }
      });

      return config;
    },
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'webpack',
    },
    specPattern: 'src/**/*.cy.{js,jsx}',
    supportFile: 'cypress/support/component.js'
  },
  retries: {
    runMode: 2,
    openMode: 0
  },
  video: true,
  screenshotOnRunFailure: true,
  chromeWebSecurity: false,
  blockHosts: [
    '*.google-analytics.com',
    '*.googletagmanager.com'
  ]
});
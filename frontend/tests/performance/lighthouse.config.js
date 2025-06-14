/**
 * Lighthouse Performance Testing Configuration
 * 
 * Automated performance testing using Google Lighthouse to ensure
 * the application meets Core Web Vitals and performance standards
 */

const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');
const fs = require('fs').promises;
const path = require('path');

// Performance thresholds based on Core Web Vitals
const PERFORMANCE_THRESHOLDS = {
  // Core Web Vitals
  'largest-contentful-paint': 2500,      // 2.5 seconds
  'first-input-delay': 100,              // 100 milliseconds  
  'cumulative-layout-shift': 0.1,        // 0.1 CLS score
  
  // Other important metrics
  'first-contentful-paint': 1800,        // 1.8 seconds
  'speed-index': 3400,                   // 3.4 seconds
  'interactive': 3800,                   // 3.8 seconds
  'total-blocking-time': 200,            // 200 milliseconds
  
  // Performance score
  'performance': 90,                     // 90/100 Lighthouse score
  
  // Accessibility score
  'accessibility': 95,                   // 95/100 accessibility score
  
  // Best practices score
  'best-practices': 95,                  // 95/100 best practices score
  
  // SEO score
  'seo': 95                             // 95/100 SEO score
};

// Romanian-specific test scenarios
const TEST_SCENARIOS = [
  {
    url: 'http://localhost:3000',
    name: 'home_page',
    description: 'Home page with featured Romanian products',
    device: 'mobile',
    throttling: 'mobileSlow4G'
  },
  {
    url: 'http://localhost:3000',
    name: 'home_page_desktop',
    description: 'Home page desktop version',
    device: 'desktop',
    throttling: 'desktopDense4G'
  },
  {
    url: 'http://localhost:3000/produse',
    name: 'products_page',
    description: 'Products listing page with Romanian products',
    device: 'mobile',
    throttling: 'mobileSlow4G'
  },
  {
    url: 'http://localhost:3000/produse?search=mere',
    name: 'search_results',
    description: 'Product search results for Romanian terms',
    device: 'mobile',
    throttling: 'mobileSlow4G'
  },
  {
    url: 'http://localhost:3000/cos',
    name: 'cart_page',
    description: 'Shopping cart page',
    device: 'mobile',
    throttling: 'mobileSlow4G'
  },
  {
    url: 'http://localhost:3000/comanda',
    name: 'checkout_page',
    description: 'Checkout page with Romanian form',
    device: 'mobile',
    throttling: 'mobileSlow4G'
  }
];

// Lighthouse configuration
const LIGHTHOUSE_CONFIG = {
  mobile: {
    extends: 'lighthouse:default',
    settings: {
      formFactor: 'mobile',
      throttling: {
        rttMs: 150,
        throughputKbps: 1638.4,
        cpuSlowdownMultiplier: 4,
        requestLatencyMs: 150,
        downloadThroughputKbps: 1638.4,
        uploadThroughputKbps: 675
      },
      screenEmulation: {
        mobile: true,
        width: 375,
        height: 667,
        deviceScaleFactor: 2,
        disabled: false
      },
      emulatedUserAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    },
    audits: [
      'first-contentful-paint',
      'largest-contentful-paint',
      'first-input-delay',
      'cumulative-layout-shift',
      'speed-index',
      'interactive',
      'total-blocking-time',
      'server-response-time',
      'render-blocking-resources',
      'unused-css-rules',
      'unused-javascript',
      'modern-image-formats',
      'uses-optimized-images',
      'uses-webp-images',
      'efficient-animated-content',
      'preload-lcp-image',
      'accessibility',
      'color-contrast',
      'image-alt',
      'label',
      'link-name',
      'meta-viewport',
      'document-title'
    ]
  },
  desktop: {
    extends: 'lighthouse:default',
    settings: {
      formFactor: 'desktop',
      throttling: {
        rttMs: 40,
        throughputKbps: 10240,
        cpuSlowdownMultiplier: 1,
        requestLatencyMs: 0,
        downloadThroughputKbps: 0,
        uploadThroughputKbps: 0
      },
      screenEmulation: {
        mobile: false,
        width: 1350,
        height: 940,
        deviceScaleFactor: 1,
        disabled: false
      }
    }
  }
};

class PerformanceTester {
  constructor() {
    this.results = [];
    this.chrome = null;
  }

  async runAllTests() {
    console.log('🚀 Starting Lighthouse performance tests...\n');
    
    try {
      // Launch Chrome
      this.chrome = await chromeLauncher.launch({
        chromeFlags: [
          '--headless',
          '--disable-gpu',
          '--no-sandbox',
          '--disable-dev-shm-usage',
          '--disable-background-timer-throttling',
          '--disable-renderer-backgrounding'
        ]
      });

      // Run tests for each scenario
      for (const scenario of TEST_SCENARIOS) {
        console.log(`📊 Testing: ${scenario.description}`);
        console.log(`🔗 URL: ${scenario.url}`);
        console.log(`📱 Device: ${scenario.device}\n`);

        const result = await this.runLighthouseTest(scenario);
        this.results.push(result);

        // Log immediate results
        this.logScenarioResults(result);
      }

      // Generate comprehensive report
      await this.generateReport();
      
      // Validate against thresholds
      const validation = this.validatePerformance();
      
      return validation;

    } finally {
      if (this.chrome) {
        await this.chrome.kill();
      }
    }
  }

  async runLighthouseTest(scenario) {
    const config = LIGHTHOUSE_CONFIG[scenario.device];
    
    try {
      const runnerResult = await lighthouse(scenario.url, {
        port: this.chrome.port,
        disableStorageReset: false,
        logLevel: 'error'
      }, config);

      const report = runnerResult.lhr;
      
      return {
        scenario,
        success: true,
        metrics: this.extractMetrics(report),
        scores: this.extractScores(report),
        opportunities: this.extractOpportunities(report),
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error(`❌ Failed to test ${scenario.name}:`, error.message);
      
      return {
        scenario,
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  extractMetrics(report) {
    const metrics = {};
    
    // Core Web Vitals
    const coreMetrics = [
      'first-contentful-paint',
      'largest-contentful-paint',
      'first-input-delay',
      'cumulative-layout-shift',
      'speed-index',
      'interactive',
      'total-blocking-time'
    ];

    for (const metricId of coreMetrics) {
      if (report.audits[metricId]) {
        const audit = report.audits[metricId];
        metrics[metricId] = {
          value: audit.numericValue || audit.score,
          score: audit.score,
          displayValue: audit.displayValue,
          description: audit.description
        };
      }
    }

    return metrics;
  }

  extractScores(report) {
    return {
      performance: Math.round(report.categories.performance.score * 100),
      accessibility: Math.round(report.categories.accessibility.score * 100),
      'best-practices': Math.round(report.categories['best-practices'].score * 100),
      seo: Math.round(report.categories.seo.score * 100)
    };
  }

  extractOpportunities(report) {
    const opportunities = [];
    
    // Performance opportunities
    const perfAudits = [
      'render-blocking-resources',
      'unused-css-rules',
      'unused-javascript',
      'modern-image-formats',
      'uses-optimized-images',
      'efficient-animated-content'
    ];

    for (const auditId of perfAudits) {
      if (report.audits[auditId] && report.audits[auditId].score < 1) {
        const audit = report.audits[auditId];
        opportunities.push({
          id: auditId,
          title: audit.title,
          description: audit.description,
          score: audit.score,
          savings: audit.details?.overallSavingsMs || 0,
          displayValue: audit.displayValue
        });
      }
    }

    return opportunities.sort((a, b) => b.savings - a.savings);
  }

  logScenarioResults(result) {
    if (!result.success) {
      console.log(`❌ Test failed: ${result.error}\n`);
      return;
    }

    const { metrics, scores } = result;
    
    console.log('📈 Performance Scores:');
    console.log(`  Performance: ${scores.performance}/100`);
    console.log(`  Accessibility: ${scores.accessibility}/100`);
    console.log(`  Best Practices: ${scores['best-practices']}/100`);
    console.log(`  SEO: ${scores.seo}/100\n`);

    console.log('⚡ Core Web Vitals:');
    if (metrics['largest-contentful-paint']) {
      console.log(`  LCP: ${metrics['largest-contentful-paint'].displayValue}`);
    }
    if (metrics['first-input-delay']) {
      console.log(`  FID: ${metrics['first-input-delay'].displayValue}`);
    }
    if (metrics['cumulative-layout-shift']) {
      console.log(`  CLS: ${metrics['cumulative-layout-shift'].displayValue}`);
    }
    
    console.log('🚀 Other Metrics:');
    if (metrics['first-contentful-paint']) {
      console.log(`  FCP: ${metrics['first-contentful-paint'].displayValue}`);
    }
    if (metrics['speed-index']) {
      console.log(`  Speed Index: ${metrics['speed-index'].displayValue}`);
    }
    if (metrics['interactive']) {
      console.log(`  Time to Interactive: ${metrics['interactive'].displayValue}`);
    }

    if (result.opportunities.length > 0) {
      console.log('\n💡 Top Optimization Opportunities:');
      result.opportunities.slice(0, 3).forEach(opp => {
        console.log(`  • ${opp.title}: ${opp.displayValue}`);
      });
    }

    console.log('\n' + '─'.repeat(60) + '\n');
  }

  validatePerformance() {
    const validation = {
      passed: true,
      failed: [],
      warnings: [],
      summary: {}
    };

    let totalTests = 0;
    let passedTests = 0;

    for (const result of this.results) {
      if (!result.success) continue;

      totalTests++;
      let scenarioPassed = true;
      const scenarioIssues = [];

      // Check scores
      for (const [category, score] of Object.entries(result.scores)) {
        const threshold = PERFORMANCE_THRESHOLDS[category];
        if (threshold && score < threshold) {
          scenarioPassed = false;
          scenarioIssues.push({
            type: 'score',
            category,
            actual: score,
            threshold,
            severity: score < threshold * 0.8 ? 'error' : 'warning'
          });
        }
      }

      // Check metrics
      for (const [metricId, metric] of Object.entries(result.metrics)) {
        const threshold = PERFORMANCE_THRESHOLDS[metricId];
        if (threshold && metric.value > threshold) {
          scenarioPassed = false;
          scenarioIssues.push({
            type: 'metric',
            metric: metricId,
            actual: metric.value,
            threshold,
            displayValue: metric.displayValue,
            severity: metric.value > threshold * 1.5 ? 'error' : 'warning'
          });
        }
      }

      if (scenarioPassed) {
        passedTests++;
      } else {
        validation.passed = false;
        validation.failed.push({
          scenario: result.scenario.name,
          issues: scenarioIssues
        });
      }
    }

    validation.summary = {
      total: totalTests,
      passed: passedTests,
      failed: totalTests - passedTests,
      passRate: totalTests > 0 ? (passedTests / totalTests) * 100 : 0
    };

    return validation;
  }

  async generateReport() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportDir = path.join(__dirname, 'reports');
    
    try {
      await fs.mkdir(reportDir, { recursive: true });
    } catch (error) {
      // Directory already exists
    }

    // Generate JSON report
    const jsonReport = {
      metadata: {
        timestamp: new Date().toISOString(),
        testCount: this.results.length,
        thresholds: PERFORMANCE_THRESHOLDS
      },
      results: this.results
    };

    const jsonPath = path.join(reportDir, `lighthouse-report-${timestamp}.json`);
    await fs.writeFile(jsonPath, JSON.stringify(jsonReport, null, 2));

    // Generate HTML report
    const htmlReport = this.generateHTMLReport(jsonReport);
    const htmlPath = path.join(reportDir, `lighthouse-report-${timestamp}.html`);
    await fs.writeFile(htmlPath, htmlReport);

    console.log(`📊 Reports generated:`);
    console.log(`  JSON: ${jsonPath}`);
    console.log(`  HTML: ${htmlPath}\n`);
  }

  generateHTMLReport(data) {
    const { metadata, results } = data;
    
    return `
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pe Foc de Lemne - Lighthouse Performance Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
        .header { background: #1a73e8; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .scenario { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #dadce0; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }
        .metric { background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #34a853; }
        .metric.warning { border-left-color: #fbbc04; }
        .metric.error { border-left-color: #ea4335; }
        .score { font-size: 24px; font-weight: bold; }
        .opportunities { margin-top: 20px; }
        .opportunity { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Pe Foc de Lemne - Performance Report</h1>
        <p>Generated: ${new Date(metadata.timestamp).toLocaleString('ro-RO')}</p>
        <p>Tests: ${metadata.testCount} scenarios</p>
    </div>

    ${results.map(result => `
        <div class="scenario">
            <h2>📊 ${result.scenario.description}</h2>
            <p><strong>URL:</strong> ${result.scenario.url}</p>
            <p><strong>Device:</strong> ${result.scenario.device}</p>
            
            ${result.success ? `
                <div class="metrics">
                    <div class="metric">
                        <div class="score">${result.scores.performance}/100</div>
                        <div>Performance</div>
                    </div>
                    <div class="metric">
                        <div class="score">${result.scores.accessibility}/100</div>
                        <div>Accessibility</div>
                    </div>
                    <div class="metric">
                        <div class="score">${result.scores['best-practices']}/100</div>
                        <div>Best Practices</div>
                    </div>
                    <div class="metric">
                        <div class="score">${result.scores.seo}/100</div>
                        <div>SEO</div>
                    </div>
                </div>

                <h3>⚡ Core Web Vitals</h3>
                <div class="metrics">
                    ${Object.entries(result.metrics).map(([key, metric]) => `
                        <div class="metric">
                            <div class="score">${metric.displayValue}</div>
                            <div>${metric.description}</div>
                        </div>
                    `).join('')}
                </div>

                ${result.opportunities.length > 0 ? `
                    <div class="opportunities">
                        <h3>💡 Optimization Opportunities</h3>
                        ${result.opportunities.map(opp => `
                            <div class="opportunity">
                                <strong>${opp.title}</strong><br>
                                ${opp.description}<br>
                                <small>Savings: ${opp.displayValue}</small>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            ` : `
                <div class="metric error">
                    <div>❌ Test Failed</div>
                    <div>${result.error}</div>
                </div>
            `}
        </div>
    `).join('')}
</body>
</html>`;
  }
}

// Main execution function
async function runPerformanceTests() {
  const tester = new PerformanceTester();
  
  try {
    const validation = await tester.runAllTests();
    
    console.log('🏁 Performance Testing Complete!\n');
    console.log('📊 Summary:');
    console.log(`  Total Tests: ${validation.summary.total}`);
    console.log(`  Passed: ${validation.summary.passed}`);
    console.log(`  Failed: ${validation.summary.failed}`);
    console.log(`  Pass Rate: ${validation.summary.passRate.toFixed(1)}%\n`);

    if (validation.passed) {
      console.log('🎉 All performance tests passed!');
      return 0;
    } else {
      console.log('❌ Some performance tests failed:');
      validation.failed.forEach(failure => {
        console.log(`\n  ${failure.scenario}:`);
        failure.issues.forEach(issue => {
          const icon = issue.severity === 'error' ? '❌' : '⚠️';
          if (issue.type === 'score') {
            console.log(`    ${icon} ${issue.category}: ${issue.actual}/100 (threshold: ${issue.threshold}/100)`);
          } else {
            console.log(`    ${icon} ${issue.metric}: ${issue.displayValue} (threshold: ${issue.threshold}ms)`);
          }
        });
      });
      return 1;
    }

  } catch (error) {
    console.error('💥 Performance testing failed:', error);
    return 1;
  }
}

module.exports = { PerformanceTester, PERFORMANCE_THRESHOLDS, TEST_SCENARIOS };

// Run if called directly
if (require.main === module) {
  runPerformanceTests().then(exitCode => {
    process.exit(exitCode);
  });
}
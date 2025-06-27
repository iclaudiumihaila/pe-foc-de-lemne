const path = require('path');

module.exports = {
  // Webpack configuration
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      // Production optimizations
      if (env === 'production') {
        // Code splitting optimization
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          splitChunks: {
            chunks: 'all',
            cacheGroups: {
              // Vendor chunks
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name: 'vendors',
                chunks: 'all',
                priority: 10,
                reuseExistingChunk: true,
              },
              // React chunks
              react: {
                test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
                name: 'react',
                chunks: 'all',
                priority: 20,
                reuseExistingChunk: true,
              },
              // Common chunks
              common: {
                name: 'common',
                minChunks: 2,
                chunks: 'all',
                priority: 5,
                reuseExistingChunk: true,
                enforce: true,
              },
              // Component chunks
              components: {
                test: /[\\/]src[\\/]components[\\/]/,
                name: 'components',
                chunks: 'all',
                priority: 15,
                reuseExistingChunk: true,
              }
            },
          },
          // Runtime chunk
          runtimeChunk: {
            name: 'runtime',
          },
          // Minimize configuration
          minimize: true,
          minimizer: [
            // Keep existing minimizers and add compression
            ...webpackConfig.optimization.minimizer,
          ],
        };

        // Performance hints
        webpackConfig.performance = {
          ...webpackConfig.performance,
          maxAssetSize: 500000, // 500KB
          maxEntrypointSize: 500000, // 500KB
          hints: 'warning',
        };

        // Add compression plugins
        const CompressionPlugin = require('compression-webpack-plugin');
        webpackConfig.plugins.push(
          new CompressionPlugin({
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/,
            threshold: 8192, // Only compress files larger than 8KB
            minRatio: 0.8,
          })
        );

        // Bundle analyzer for development insights
        if (process.env.ANALYZE) {
          const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
          webpackConfig.plugins.push(
            new BundleAnalyzerPlugin({
              analyzerMode: 'static',
              openAnalyzer: false,
              reportFilename: 'bundle-report.html',
            })
          );
        }
      }

      // Resolve configuration
      webpackConfig.resolve = {
        ...webpackConfig.resolve,
        alias: {
          ...webpackConfig.resolve.alias,
          '@': path.resolve(__dirname, 'src'),
          '@components': path.resolve(__dirname, 'src/components'),
          '@pages': path.resolve(__dirname, 'src/pages'),
          '@hooks': path.resolve(__dirname, 'src/hooks'),
          '@utils': path.resolve(__dirname, 'src/utils'),
          '@services': path.resolve(__dirname, 'src/services'),
          '@contexts': path.resolve(__dirname, 'src/contexts'),
          '@styles': path.resolve(__dirname, 'src/styles'),
        },
      };

      // Module rules for optimization
      const oneOfRule = webpackConfig.module.rules.find(rule => rule.oneOf);
      if (oneOfRule) {
        // Add image optimization
        const imageRule = {
          test: /\.(png|jpe?g|gif|svg)$/i,
          use: [
            {
              loader: 'file-loader',
              options: {
                outputPath: 'static/media',
                name: '[name].[contenthash:8].[ext]',
              },
            },
            {
              loader: 'image-webpack-loader',
              options: {
                mozjpeg: {
                  progressive: true,
                  quality: 85,
                },
                optipng: {
                  enabled: false,
                },
                pngquant: {
                  quality: [0.6, 0.8],
                },
                gifsicle: {
                  interlaced: false,
                },
                webp: {
                  quality: 85,
                },
              },
            },
          ],
        };

        // Insert before the file loader
        const fileLoaderIndex = oneOfRule.oneOf.findIndex(rule => 
          rule.loader && rule.loader.includes('file-loader')
        );
        if (fileLoaderIndex >= 0) {
          oneOfRule.oneOf.splice(fileLoaderIndex, 0, imageRule);
        }
      }

      return webpackConfig;
    },
  },

  // Babel configuration
  babel: {
    plugins: [
      // Add babel plugins for optimization
      ...(process.env.NODE_ENV === 'production' ? [
        ['babel-plugin-transform-remove-console', { 
          exclude: ['error', 'warn'] 
        }],
      ] : []),
    ],
    presets: [],
  },

  // ESLint configuration
  eslint: {
    enable: true,
    mode: 'extends',
    configure: {
      rules: {
        // Performance-related ESLint rules
        'react-hooks/exhaustive-deps': 'warn',
        'no-unused-vars': 'warn',
        'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      },
    },
  },

  // Development server configuration
  devServer: {
    port: 3000,
    open: false,
    compress: true,
    historyApiFallback: true,
    allowedHosts: [
      'localhost',
      '.railway.app',
      '.up.railway.app'
    ],
    client: {
      overlay: {
        errors: true,
        warnings: false,
      },
    },
    // Performance monitoring in development
    onBeforeSetupMiddleware: (devServer) => {
      devServer.app.get('/api/performance', (req, res) => {
        res.json({
          timestamp: Date.now(),
          message: 'Performance monitoring endpoint',
        });
      });
    },
  },
};
module.exports = {
  testEnvironment: 'node',
  collectCoverage: true,
  collectCoverageFrom: ['hipaah/**/*.js', '!**/node_modules/**', '!**/tests/**'],
  coverageDirectory: 'coverage',
  coverageReporters: ['lcov', 'text', 'text-summary'],
  testMatch: ['**/tests/**/*.test.js'],
  verbose: true
};
const fs = require('fs');
const path = require('path');
const { SafeLogger } = require('../hipaah');

// Create a temp directory for log file testing
const TEMP_DIR = path.join(__dirname, 'temp');
const ACCESS_LOG_PATH = path.join(TEMP_DIR, 'access_log.jsonl');
const JUSTIFICATION_LOG_PATH = path.join(TEMP_DIR, 'justification_log.jsonl');

// Create temp directory if it doesn't exist
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
}

// Sample data for testing
const PHI_DATA = {
  name: 'John Smith',
  diagnosis: 'Diabetes',
  insurance_number: '123-45-6789',
  notes: 'Patient reported headaches.'
};

describe('SafeLogger', () => {
  // Capture console output
  let consoleLogSpy;
  let consoleWarnSpy;
  let consoleErrorSpy;
  
  beforeEach(() => {
    // Reset log files
    if (fs.existsSync(ACCESS_LOG_PATH)) {
      fs.unlinkSync(ACCESS_LOG_PATH);
    }
    if (fs.existsSync(JUSTIFICATION_LOG_PATH)) {
      fs.unlinkSync(JUSTIFICATION_LOG_PATH);
    }
    
    // Spy on console methods
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
  });
  
  afterEach(() => {
    // Restore console methods
    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });
  
  describe('constructor', () => {
    it('should create a SafeLogger instance with default options', () => {
      const logger = new SafeLogger();
      expect(logger).toBeInstanceOf(SafeLogger);
      expect(logger.maskedFields).toEqual([]);
      expect(logger.options.writeToFile).toBe(false);
    });
    
    it('should create a SafeLogger with specified masked fields', () => {
      const logger = new SafeLogger(['diagnosis', 'insurance_number']);
      expect(logger.maskedFields).toEqual(['diagnosis', 'insurance_number']);
    });
    
    it('should create a SafeLogger with file writing enabled', () => {
      const logger = new SafeLogger([], { 
        writeToFile: true,
        logFilePath: ACCESS_LOG_PATH
      });
      
      expect(logger.options.writeToFile).toBe(true);
      expect(logger.fs).toBeDefined();
    });
  });
  
  describe('logging methods', () => {
    it('should log info messages to console', () => {
      const logger = new SafeLogger();
      logger.info('Test info message');
      
      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('INFO'));
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Test info message'));
    });
    
    it('should log warning messages to console', () => {
      const logger = new SafeLogger();
      logger.warning('Test warning message');
      
      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('WARNING'));
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Test warning message'));
    });
    
    it('should log error messages to console', () => {
      const logger = new SafeLogger();
      logger.error('Test error message');
      
      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('ERROR'));
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Test error message'));
    });
    
    it('should mask PHI fields in logged data', () => {
      const logger = new SafeLogger(['diagnosis', 'insurance_number']);
      logger.info('Patient record accessed', PHI_DATA);
      
      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      
      const loggedJson = JSON.parse(consoleLogSpy.mock.calls[0][0]);
      
      // These fields should be masked
      expect(loggedJson.data.diagnosis).toBe('***');
      expect(loggedJson.data.insurance_number).toBe('***');
      
      // These fields should not be masked
      expect(loggedJson.data.name).toBe(PHI_DATA.name);
      expect(loggedJson.data.notes).toBe(PHI_DATA.notes);
    });
  });
  
  describe('file logging', () => {
    it('should write logs to file when enabled', () => {
      const logger = new SafeLogger(['diagnosis'], { 
        writeToFile: true,
        logFilePath: ACCESS_LOG_PATH
      });
      
      logger.info('Test file logging', PHI_DATA);
      
      // Check file exists
      expect(fs.existsSync(ACCESS_LOG_PATH)).toBe(true);
      
      // Read file contents
      const fileContents = fs.readFileSync(ACCESS_LOG_PATH, 'utf8');
      const logEntries = fileContents.trim().split('\n').map(JSON.parse);
      
      // Should have one entry
      expect(logEntries.length).toBe(1);
      
      // Check entry contents
      expect(logEntries[0].level).toBe('INFO');
      expect(logEntries[0].message).toBe('Test file logging');
      expect(logEntries[0].data.diagnosis).toBe('***');
    });
    
    it('should write multiple log entries to the same file', () => {
      const logger = new SafeLogger([], { 
        writeToFile: true,
        logFilePath: ACCESS_LOG_PATH
      });
      
      logger.info('First log');
      logger.info('Second log');
      logger.warning('Third log');
      
      // Check file exists
      expect(fs.existsSync(ACCESS_LOG_PATH)).toBe(true);
      
      // Read file contents
      const fileContents = fs.readFileSync(ACCESS_LOG_PATH, 'utf8');
      const logEntries = fileContents.trim().split('\n').map(JSON.parse);
      
      // Should have three entries
      expect(logEntries.length).toBe(3);
      
      // Check first entry
      expect(logEntries[0].level).toBe('INFO');
      expect(logEntries[0].message).toBe('First log');
      
      // Check last entry
      expect(logEntries[2].level).toBe('WARNING');
      expect(logEntries[2].message).toBe('Third log');
    });
  });
  
  describe('justification logging', () => {
    it('should log justifications to separate file', () => {
      const logger = new SafeLogger([], { 
        writeToFile: true,
        logFilePath: ACCESS_LOG_PATH
      });
      
      logger.justification(
        'doctor',
        'treatment',
        'patient-123',
        'Emergency consultation'
      );
      
      // Check both files exist
      expect(fs.existsSync(ACCESS_LOG_PATH)).toBe(true);
      expect(fs.existsSync(JUSTIFICATION_LOG_PATH)).toBe(true);
      
      // Read justification file
      const fileContents = fs.readFileSync(JUSTIFICATION_LOG_PATH, 'utf8');
      const entries = fileContents.trim().split('\n').map(JSON.parse);
      
      // Should have one entry
      expect(entries.length).toBe(1);
      
      // Check entry contents
      expect(entries[0].role).toBe('doctor');
      expect(entries[0].intent).toBe('treatment');
      expect(entries[0].resource_id).toBe('patient-123');
      expect(entries[0].justification).toBe('Emergency consultation');
      expect(entries[0].timestamp).toBeDefined();
    });
    
    it('should also log a regular info message when justification is recorded', () => {
      const logger = new SafeLogger([], { 
        writeToFile: true,
        logFilePath: ACCESS_LOG_PATH
      });
      
      logger.justification(
        'doctor',
        'treatment',
        'patient-123',
        'Emergency consultation'
      );
      
      // Check info was logged to console
      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      
      // Read access log file
      const fileContents = fs.readFileSync(ACCESS_LOG_PATH, 'utf8');
      const entries = fileContents.trim().split('\n').map(JSON.parse);
      
      // Should have one entry
      expect(entries.length).toBe(1);
      
      // Check info log mentions the justification
      expect(entries[0].level).toBe('INFO');
      expect(entries[0].message).toContain('Access justified by doctor');
    });
  });
  
  describe('custom log handler', () => {
    it('should use custom log handler when provided', () => {
      const customHandler = jest.fn();
      
      const logger = new SafeLogger([], { 
        logHandler: customHandler
      });
      
      logger.info('Custom handler test');
      
      // Custom handler should be called
      expect(customHandler).toHaveBeenCalledTimes(1);
      
      // Console log should not be called
      expect(consoleLogSpy).not.toHaveBeenCalled();
      
      // Check handler was called with correct data
      const logEntry = customHandler.mock.calls[0][0];
      expect(logEntry.level).toBe('INFO');
      expect(logEntry.message).toBe('Custom handler test');
    });
  });
});
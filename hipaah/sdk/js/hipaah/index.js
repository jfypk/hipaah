const fs = require('fs');
const yaml = require('js-yaml');
const { maskData } = require('./utils');

// Constant for masked values
const MASKED = '***';

/**
 * Main client class for the HIPAAH SDK
 */
class HipaahClient {
  /**
   * Create a new HipaahClient instance
   * @param {string} policyPath - Optional path to a policy YAML file
   */
  constructor(policyPath = null) {
    this.policies = null;
    
    if (policyPath) {
      this.loadPolicy(policyPath);
    }
  }

  /**
   * Load policies from a YAML file
   * @param {string} policyPath - Path to the policy file
   * @returns {Object} The loaded policies
   */
  loadPolicy(policyPath) {
    try {
      const fileContents = fs.readFileSync(policyPath, 'utf8');
      this.policies = yaml.load(fileContents);
      return this.policies;
    } catch (error) {
      throw new Error(`Failed to load policy file: ${error.message}`);
    }
  }

  /**
   * Evaluate a resource against the loaded policies
   * @param {Object} resource - The resource to evaluate
   * @param {string} role - The user role
   * @param {string} intent - The access intent
   * @param {Object} attributes - Optional attributes for policy evaluation
   * @returns {Object} The result of policy evaluation
   */
  evaluate(resource, role, intent, attributes = {}) {
    if (!this.policies) {
      throw new Error('No policies loaded. Call loadPolicy first.');
    }

    return this._evaluatePolicy({
      role,
      intent,
      attributes,
      resource
    }, this.policies);
  }

  /**
   * Evaluate multiple resources against the loaded policies
   * @param {Array<Object>} resources - The resources to evaluate
   * @param {string} role - The user role
   * @param {string} intent - The access intent
   * @param {Object} attributes - Optional attributes for policy evaluation
   * @returns {Array<Object>} The results of policy evaluation
   */
  batchEvaluate(resources, role, intent, attributes = {}) {
    return resources.map(resource => this.evaluate(resource, role, intent, attributes));
  }

  /**
   * Internal method to evaluate a policy
   * @private
   * @param {Object} request - The policy request
   * @param {Array} policies - The policies to evaluate against
   * @returns {Object} The filtered resource
   */
  _evaluatePolicy(request, policies) {
    const { role, intent, attributes, resource } = request;
    
    // Match policy by role and intent, and evaluate conditions
    for (const policy of policies) {
      if (policy.role !== role || policy.intent !== intent) {
        continue;
      }
      
      // Check conditions if they exist
      if (policy.conditions) {
        const matchesConditions = Object.entries(policy.conditions).every(
          ([key, value]) => attributes[key] === value
        );
        
        if (!matchesConditions) {
          continue;
        }
      }
      
      // Apply policy (allow, mask, deny)
      const result = {};
      
      // Process each field in the resource based on policy
      for (const [key, value] of Object.entries(resource)) {
        // Check explicitly denied fields first
        if (policy.deny && policy.deny.includes(key)) {
          // Skip this field entirely
          continue;
        } 
        // Then check for masked fields
        else if (policy.mask && policy.mask.includes(key)) {
          result[key] = MASKED;
        } 
        // Finally check allowed fields
        else if (
          policy.allow === '*' || 
          (policy.allow && policy.allow.includes(key))
        ) {
          result[key] = value;
        }
        // If not explicitly mentioned in any list, it's implicitly denied
      }
      
      // Add expiry metadata if justification provided
      if (attributes.justification && policy.justification_ttl) {
        const expiry = new Date();
        expiry.setMinutes(expiry.getMinutes() + policy.justification_ttl);
        result._meta = {
          expires_at: expiry.toISOString()
        };
      }
      
      return result;
    }
    
    // Default deny-all if no matching policy found
    return {};
  }
}

/**
 * Client for interacting with the HIPAAH API
 */
class ApiClient extends HipaahClient {
  /**
   * Create a new ApiClient instance
   * @param {string} apiUrl - URL of the HIPAAH API
   * @param {string} apiKey - Optional API key for authentication
   * @param {string} policyPath - Optional path to a policy file for local evaluation fallback
   */
  constructor(apiUrl, apiKey = null, policyPath = null) {
    super(policyPath);
    this.apiUrl = apiUrl.endsWith('/') ? apiUrl : `${apiUrl}/`;
    this.apiKey = apiKey || process.env.HIPAAH_API_KEY;
    
    // Check for fetch compatibility
    if (typeof fetch !== 'function') {
      try {
        // Node.js environment - try to load node-fetch
        if (typeof global !== 'undefined' && typeof require === 'function') {
          this.fetch = require('node-fetch');
        }
      } catch (error) {
        console.warn('node-fetch not found. Please install it with: npm install node-fetch');
        this.fetch = null;
      }
    } else {
      // Browser or modern Node.js environment
      this.fetch = fetch;
    }
  }

  /**
   * Evaluate a resource against the remote API
   * @param {Object} resource - The resource to evaluate
   * @param {string} role - The user role
   * @param {string} intent - The access intent
   * @param {Object} attributes - Optional attributes for policy evaluation
   * @returns {Promise<Object>} The result of policy evaluation
   */
  async remoteEvaluate(resource, role, intent, attributes = {}) {
    // Prepare the request payload
    const payload = {
      role,
      intent,
      attributes,
      resource
    };
    
    // If fetch is available, use it to make the API request
    if (this.fetch) {
      try {
        const response = await this.fetch(`${this.apiUrl}evaluate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
            'X-HIPAAH-CLIENT': 'js-sdk'
          },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API error (${response.status}): ${errorText}`);
        }
        
        return await response.json();
      } catch (error) {
        // If API request fails, log warning and fall back to local evaluation
        console.warn(`API evaluation failed: ${error.message}. Falling back to local evaluation.`);
        
        // Only perform local evaluation if policies are loaded
        if (this.policies) {
          return this.evaluate(resource, role, intent, attributes);
        } else {
          throw new Error('API evaluation failed and no local policies are loaded for fallback.');
        }
      }
    } else {
      // If fetch is not available, fall back to local evaluation
      console.warn('HTTP client not available for API request. Falling back to local evaluation.');
      
      // Only perform local evaluation if policies are loaded
      if (this.policies) {
        return this.evaluate(resource, role, intent, attributes);
      } else {
        throw new Error('HTTP client not available and no local policies are loaded for fallback.');
      }
    }
  }
  
  /**
   * Record an access in the audit log
   * @param {string} role - The user role
   * @param {string} intent - The access intent
   * @param {string} resourceId - Identifier for the resource being accessed
   * @param {string} justification - Reason for the access
   * @returns {Promise<Object>} The audit log entry
   */
  async logAccess(role, intent, resourceId, justification = null) {
    // Skip if fetch is not available
    if (!this.fetch) {
      console.warn('HTTP client not available for API request. Access logging skipped.');
      return null;
    }
    
    const payload = {
      role,
      intent,
      resource_id: resourceId,
      justification,
      timestamp: new Date().toISOString()
    };
    
    try {
      const response = await this.fetch(`${this.apiUrl}log`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
          'X-HIPAAH-CLIENT': 'js-sdk'
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        console.warn(`Failed to log access: ${response.status} ${response.statusText}`);
        return null;
      }
      
      return await response.json();
    } catch (error) {
      console.warn(`Failed to log access: ${error.message}`);
      return null;
    }
  }
}

/**
 * Logger that safely masks sensitive fields to avoid exposing PHI in logs
 */
class SafeLogger {
  /**
   * Create a new SafeLogger instance
   * @param {Array<string>} maskedFields - Array of field names to mask
   * @param {Object} options - Additional options
   * @param {boolean} options.writeToFile - Whether to write logs to a file
   * @param {string} options.logFilePath - Path to the log file
   * @param {Function} options.logHandler - Custom log handler function
   */
  constructor(maskedFields = [], options = {}) {
    this.maskedFields = maskedFields;
    this.options = {
      writeToFile: false,
      logFilePath: './data/access_log.jsonl',
      ...options
    };

    // Set up file logging if enabled
    if (this.options.writeToFile) {
      try {
        this.fs = require('fs');
        
        // Create directory if it doesn't exist
        const path = require('path');
        const dir = path.dirname(this.options.logFilePath);
        
        if (!this.fs.existsSync(dir)) {
          this.fs.mkdirSync(dir, { recursive: true });
        }
      } catch (error) {
        console.warn(`Failed to set up file logging: ${error.message}`);
        this.options.writeToFile = false;
      }
    }
  }

  /**
   * Log an info message
   * @param {string} message - The message to log
   * @param {Object} data - Optional data to include in the log
   */
  info(message, data = null) {
    this._log('INFO', message, data);
  }

  /**
   * Log a warning message
   * @param {string} message - The message to log
   * @param {Object} data - Optional data to include in the log
   */
  warning(message, data = null) {
    this._log('WARNING', message, data);
  }

  /**
   * Log an error message
   * @param {string} message - The message to log
   * @param {Object} data - Optional data to include in the log
   */
  error(message, data = null) {
    this._log('ERROR', message, data);
  }

  /**
   * Log an access justification
   * @param {string} role - The role accessing the data
   * @param {string} intent - The intent of the access
   * @param {string} resourceId - Identifier for the resource
   * @param {string} justification - Reason for the access
   */
  justification(role, intent, resourceId, justification) {
    const justificationData = {
      role,
      intent,
      resource_id: resourceId,
      justification,
      timestamp: new Date().toISOString()
    };
    
    this._writeToJustificationLog(justificationData);
    this.info(`Access justified by ${role} for ${intent}`, { resource_id: resourceId });
  }

  /**
   * Internal method to log a message
   * @private
   * @param {string} level - The log level
   * @param {string} message - The message to log
   * @param {Object} data - Optional data to include in the log
   */
  _log(level, message, data) {
    const timestamp = new Date().toISOString();
    
    // Apply masking to any PHI data before logging
    const maskedData = data ? maskData(data, this.maskedFields) : null;
    
    const logEntry = {
      timestamp,
      level,
      message,
      data: maskedData
    };
    
    // Use custom log handler if provided
    if (typeof this.options.logHandler === 'function') {
      this.options.logHandler(logEntry);
      return;
    }
    
    // Write to console
    console.log(JSON.stringify(logEntry));
    
    // Write to file if enabled
    if (this.options.writeToFile && this.fs) {
      try {
        this.fs.appendFileSync(
          this.options.logFilePath,
          JSON.stringify(logEntry) + '\n',
          'utf8'
        );
      } catch (error) {
        console.error(`Failed to write to log file: ${error.message}`);
      }
    }
  }
  
  /**
   * Write a justification entry to the justification log
   * @private
   * @param {Object} data - The justification data to log
   */
  _writeToJustificationLog(data) {
    // Skip if file writing is not enabled
    if (!this.options.writeToFile || !this.fs) {
      return;
    }
    
    try {
      const justificationLogPath = this.options.logFilePath.replace(
        'access_log.jsonl',
        'justification_log.jsonl'
      );
      
      this.fs.appendFileSync(
        justificationLogPath,
        JSON.stringify(data) + '\n',
        'utf8'
      );
    } catch (error) {
      console.error(`Failed to write to justification log: ${error.message}`);
    }
  }
}

// Utility functions
const utils = {
  /**
   * Load a resource from a JSON file
   * @param {string} filePath - Path to the JSON file
   * @returns {Object} The loaded resource
   */
  loadResourceFromFile: (filePath) => {
    try {
      const fileContents = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(fileContents);
    } catch (error) {
      throw new Error(`Failed to load resource file: ${error.message}`);
    }
  },
  
  /**
   * Save a resource to a JSON file
   * @param {Object} resource - The resource to save
   * @param {string} filePath - Path to save the JSON file
   */
  saveResourceToFile: (resource, filePath) => {
    try {
      const jsonString = JSON.stringify(resource, null, 2);
      fs.writeFileSync(filePath, jsonString, 'utf8');
    } catch (error) {
      throw new Error(`Failed to save resource file: ${error.message}`);
    }
  },
  
  /**
   * Mask PHI fields in data
   * @param {Object} data - The data containing PHI fields
   * @param {Array<string>} fieldsToMask - List of field names to mask
   * @returns {Object} A copy of the data with PHI fields masked
   */
  maskPhiFields: (data, fieldsToMask) => {
    return maskData(data, fieldsToMask);
  },
  
  /**
   * Merge multiple policy files into one
   * @param {Array<string>} policyFiles - List of policy file paths
   * @returns {Object} A merged policy object
   */
  mergePolicies: (policyFiles) => {
    const merged = [];
    
    for (const filePath of policyFiles) {
      try {
        const fileContents = fs.readFileSync(filePath, 'utf8');
        const policies = yaml.load(fileContents);
        
        if (Array.isArray(policies)) {
          merged.push(...policies);
        } else {
          throw new Error(`Policy file ${filePath} did not contain an array of policies`);
        }
      } catch (error) {
        throw new Error(`Failed to merge policy file ${filePath}: ${error.message}`);
      }
    }
    
    return merged;
  },
  
  /**
   * Generate synthetic PHI data for screenshots and demos
   * @param {Object} template - Template object with field structure
   * @param {boolean} watermark - Whether to add watermark indicators
   * @returns {Object} Synthetic data that looks like real PHI but is fake
   */
  generateSyntheticData: (template, watermark = true) => {
    // This is a simple synthetic data generator
    // In a real implementation, you would use a more sophisticated library like Faker
    
    const syntheticData = { ...template };
    
    // Generate fake names based on pattern
    if ('name' in template) {
      const names = [
        'John Smith', 'Lisa Chang', 'Sarah Johnson', 
        'Michael Williams', 'David Martinez', 'Maria Rodriguez'
      ];
      syntheticData.name = names[Math.floor(Math.random() * names.length)];
    }
    
    // Generate fake DOBs
    if ('dob' in template) {
      const year = 1960 + Math.floor(Math.random() * 40);
      const month = 1 + Math.floor(Math.random() * 12);
      const day = 1 + Math.floor(Math.random() * 28);
      syntheticData.dob = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    }
    
    // Generate fake diagnoses
    if ('diagnosis' in template) {
      const diagnoses = [
        'Hypertension', 'Type 2 Diabetes', 'Asthma', 
        'Anxiety Disorder', 'Migraine', 'Arthritis'
      ];
      syntheticData.diagnosis = diagnoses[Math.floor(Math.random() * diagnoses.length)];
    }
    
    // Generate fake insurance numbers
    if ('insurance_number' in template) {
      const prefix = Math.floor(Math.random() * 900) + 100;
      const middle = Math.floor(Math.random() * 90) + 10;
      const suffix = Math.floor(Math.random() * 9000) + 1000;
      syntheticData.insurance_number = `${prefix}-${middle}-${suffix}`;
    }
    
    // Add watermark if requested
    if (watermark) {
      syntheticData._meta = {
        synthetic: true,
        generated_at: new Date().toISOString(),
        notice: 'SYNTHETIC DATA - NOT REAL PHI - FOR DEMO PURPOSES ONLY'
      };
    }
    
    return syntheticData;
  },
  
  /**
   * Sanitize an LLM prompt to make it HIPAA-compliant
   * @param {string} prompt - The original prompt that might contain PHI
   * @param {Array<string>} phiPatterns - Patterns or terms to look for and mask
   * @returns {string} A sanitized prompt safe to send to an LLM
   */
  sanitizeLlmPrompt: (prompt, phiPatterns = []) => {
    let sanitized = prompt;
    
    // Add default PHI patterns if none provided
    if (!phiPatterns.length) {
      phiPatterns = [
        // SSN pattern
        /\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b/g,
        // Phone pattern
        /\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b/g,
        // Email pattern
        /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
        // DOB pattern
        /\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/g,
        /\b\d{4}-\d{1,2}-\d{1,2}\b/g,
      ];
    }
    
    // Replace patterns with [REDACTED]
    for (const pattern of phiPatterns) {
      if (pattern instanceof RegExp) {
        sanitized = sanitized.replace(pattern, '[REDACTED]');
      } else if (typeof pattern === 'string') {
        sanitized = sanitized.replace(new RegExp(pattern, 'gi'), '[REDACTED]');
      }
    }
    
    return sanitized;
  }
};

module.exports = {
  HipaahClient,
  ApiClient,
  SafeLogger,
  MASKED,
  loadResourceFromFile: utils.loadResourceFromFile,
  saveResourceToFile: utils.saveResourceToFile,
  maskPhiFields: utils.maskPhiFields,
  mergePolicies: utils.mergePolicies,
  generateSyntheticData: utils.generateSyntheticData,
  sanitizeLlmPrompt: utils.sanitizeLlmPrompt
};
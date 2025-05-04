const fs = require('fs');
const path = require('path');
const {
  maskPhiFields,
  loadResourceFromFile,
  saveResourceToFile,
  mergePolicies,
  generateSyntheticData,
  sanitizeLlmPrompt
} = require('../hipaah');

// Path to test fixtures
const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const POLICY_PATH = path.join(FIXTURES_DIR, 'sample_policy.yaml');
const RESOURCE_PATH = path.join(FIXTURES_DIR, 'sample_resource.json');

// Create a temp directory for file tests
const TEMP_DIR = path.join(__dirname, 'temp');
const TEMP_FILE_PATH = path.join(TEMP_DIR, 'temp_resource.json');

// Create temp directory if it doesn't exist
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
}

describe('Utility Functions', () => {
  describe('maskPhiFields', () => {
    it('should mask specified fields', () => {
      const data = {
        name: 'John Smith',
        dob: '1980-01-01',
        diagnosis: 'Hypertension',
        insurance_number: '123-45-6789'
      };
      
      const fieldsToMask = ['diagnosis', 'insurance_number'];
      const result = maskPhiFields(data, fieldsToMask);
      
      // Masked fields should be replaced with '***'
      expect(result.diagnosis).toBe('***');
      expect(result.insurance_number).toBe('***');
      
      // Non-masked fields should remain unchanged
      expect(result.name).toBe('John Smith');
      expect(result.dob).toBe('1980-01-01');
      
      // Original data should be unchanged
      expect(data.diagnosis).toBe('Hypertension');
    });
    
    it('should handle nested objects', () => {
      const data = {
        name: 'John Smith',
        medical: {
          diagnosis: 'Hypertension',
          insurance_number: '123-45-6789'
        }
      };
      
      const fieldsToMask = ['diagnosis', 'insurance_number'];
      const result = maskPhiFields(data, fieldsToMask);
      
      // Masked fields in nested objects should be replaced
      expect(result.medical.diagnosis).toBe('***');
      expect(result.medical.insurance_number).toBe('***');
      
      // Non-masked fields should remain unchanged
      expect(result.name).toBe('John Smith');
    });
    
    it('should handle arrays', () => {
      const data = [
        {
          name: 'John Smith',
          diagnosis: 'Hypertension'
        },
        {
          name: 'Jane Doe',
          diagnosis: 'Diabetes'
        }
      ];
      
      const fieldsToMask = ['diagnosis'];
      const result = maskPhiFields(data, fieldsToMask);
      
      // Masked fields in arrays should be replaced
      expect(result[0].diagnosis).toBe('***');
      expect(result[1].diagnosis).toBe('***');
      
      // Non-masked fields should remain unchanged
      expect(result[0].name).toBe('John Smith');
      expect(result[1].name).toBe('Jane Doe');
    });
    
    it('should return data unchanged if no fields to mask', () => {
      const data = {
        name: 'John Smith',
        dob: '1980-01-01'
      };
      
      const result = maskPhiFields(data, []);
      
      // Data should be unchanged
      expect(result).toEqual(data);
    });
    
    it('should handle non-object data', () => {
      const stringValue = 'Just a string';
      const numberValue = 42;
      
      // Should return primitives unchanged
      expect(maskPhiFields(stringValue, ['anything'])).toBe(stringValue);
      expect(maskPhiFields(numberValue, ['anything'])).toBe(numberValue);
      expect(maskPhiFields(null, ['anything'])).toBeNull();
    });
  });
  
  describe('loadResourceFromFile', () => {
    it('should load JSON resource from file', () => {
      const resource = loadResourceFromFile(RESOURCE_PATH);
      
      expect(resource).toBeDefined();
      expect(resource.name).toBe('Lisa Chang');
      expect(resource.diagnosis).toBe('Asthma');
    });
    
    it('should throw error for non-existent file', () => {
      expect(() => {
        loadResourceFromFile('nonexistent-file.json');
      }).toThrow();
    });
  });
  
  describe('saveResourceToFile', () => {
    it('should save resource to JSON file', () => {
      const resource = {
        name: 'New Patient',
        diagnosis: 'Migraine',
        insurance_number: '987-65-4321'
      };
      
      saveResourceToFile(resource, TEMP_FILE_PATH);
      
      // File should exist
      expect(fs.existsSync(TEMP_FILE_PATH)).toBe(true);
      
      // Read file back and check content
      const savedResource = JSON.parse(fs.readFileSync(TEMP_FILE_PATH, 'utf8'));
      expect(savedResource).toEqual(resource);
    });
  });
  
  describe('mergePolicies', () => {
    it('should merge multiple policy files', () => {
      // For this test, we'll use the same policy file twice to simulate merging
      const policyFiles = [POLICY_PATH, POLICY_PATH];
      
      const merged = mergePolicies(policyFiles);
      
      // Result should be an array
      expect(Array.isArray(merged)).toBe(true);
      
      // Length should be double the original policy count
      const singlePolicyCount = 4; // based on our sample_policy.yaml
      expect(merged.length).toBe(singlePolicyCount * 2);
      
      // Should contain policies for expected roles
      const roles = merged.map(p => p.role);
      expect(roles).toContain('receptionist');
      expect(roles).toContain('nurse');
      expect(roles).toContain('doctor');
    });
    
    it('should throw error for invalid policy file', () => {
      expect(() => {
        mergePolicies(['nonexistent-file.yaml']);
      }).toThrow();
    });
  });
  
  describe('generateSyntheticData', () => {
    it('should generate synthetic data based on template', () => {
      const template = {
        name: true,
        dob: true,
        diagnosis: true,
        insurance_number: true
      };
      
      const result = generateSyntheticData(template);
      
      // Should generate all fields in template
      expect(result.name).toBeDefined();
      expect(result.dob).toBeDefined();
      expect(result.diagnosis).toBeDefined();
      expect(result.insurance_number).toBeDefined();
      
      // Should add watermark
      expect(result._meta).toBeDefined();
      expect(result._meta.synthetic).toBe(true);
    });
    
    it('should generate synthetic data without watermark if requested', () => {
      const template = {
        name: true,
        diagnosis: true
      };
      
      const result = generateSyntheticData(template, false);
      
      // Should generate requested fields
      expect(result.name).toBeDefined();
      expect(result.diagnosis).toBeDefined();
      
      // Should not add watermark
      expect(result._meta).toBeUndefined();
    });
  });
  
  describe('sanitizeLlmPrompt', () => {
    it('should sanitize SSN patterns in prompts', () => {
      const prompt = 'The patient SSN is 123-45-6789 and DOB is 01/01/1980';
      const result = sanitizeLlmPrompt(prompt);
      
      expect(result).toContain('[REDACTED]');
      expect(result).not.toContain('123-45-6789');
    });
    
    it('should sanitize multiple patterns in prompts', () => {
      const prompt = 'The patient SSN is 123-45-6789, email is patient@example.com, and phone is 555-123-4567';
      const result = sanitizeLlmPrompt(prompt);
      
      expect(result).toContain('[REDACTED]');
      expect(result).not.toContain('123-45-6789');
      expect(result).not.toContain('patient@example.com');
      expect(result).not.toContain('555-123-4567');
    });
    
    it('should sanitize custom patterns', () => {
      const prompt = 'The patient has a custom ID ABC-12345-Z';
      const result = sanitizeLlmPrompt(prompt, [/ABC-\d+-Z/]);
      
      expect(result).toContain('[REDACTED]');
      expect(result).not.toContain('ABC-12345-Z');
    });
    
    it('should handle string patterns', () => {
      const prompt = 'The patient name is John Smith';
      const result = sanitizeLlmPrompt(prompt, ['John Smith']);
      
      expect(result).toContain('[REDACTED]');
      expect(result).not.toContain('John Smith');
    });
  });
});
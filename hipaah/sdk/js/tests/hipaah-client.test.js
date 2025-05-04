const fs = require('fs');
const path = require('path');
const { HipaahClient, MASKED } = require('../hipaah');

// Path to test fixtures
const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const POLICY_PATH = path.join(FIXTURES_DIR, 'sample_policy.yaml');
const RESOURCE_PATH = path.join(FIXTURES_DIR, 'sample_resource.json');

describe('HipaahClient', () => {
  let client;
  let resource;

  beforeEach(() => {
    // Create a new client before each test
    client = new HipaahClient(POLICY_PATH);
    
    // Load the test resource
    resource = JSON.parse(fs.readFileSync(RESOURCE_PATH, 'utf8'));
  });

  describe('constructor', () => {
    it('should create a client instance', () => {
      expect(client).toBeInstanceOf(HipaahClient);
    });

    it('should load policies when path is provided', () => {
      expect(client.policies).toBeDefined();
      expect(Array.isArray(client.policies)).toBe(true);
      expect(client.policies.length).toBeGreaterThan(0);
    });

    it('should create a client without policies when no path is provided', () => {
      const emptyClient = new HipaahClient();
      expect(emptyClient.policies).toBeNull();
    });
  });

  describe('loadPolicy', () => {
    it('should load policies from a YAML file', () => {
      const emptyClient = new HipaahClient();
      const policies = emptyClient.loadPolicy(POLICY_PATH);
      
      expect(policies).toBeDefined();
      expect(Array.isArray(policies)).toBe(true);
      expect(policies.length).toBeGreaterThan(0);
    });

    it('should throw an error for invalid policy file', () => {
      const emptyClient = new HipaahClient();
      expect(() => {
        emptyClient.loadPolicy('nonexistent-file.yaml');
      }).toThrow();
    });
  });

  describe('evaluate', () => {
    it('should throw an error if no policies are loaded', () => {
      const emptyClient = new HipaahClient();
      expect(() => {
        emptyClient.evaluate(resource, 'receptionist', 'treatment');
      }).toThrow('No policies loaded');
    });

    it('should evaluate policy for receptionist role', () => {
      const result = client.evaluate(resource, 'receptionist', 'treatment', { active_shift_only: true });
      
      // Should allow name, dob, appointment_time
      expect(result.name).toBe(resource.name);
      expect(result.dob).toBe(resource.dob);
      expect(result.appointment_time).toBe(resource.appointment_time);
      
      // Should mask diagnosis, notes
      expect(result.diagnosis).toBe(MASKED);
      expect(result.notes).toBe(MASKED);
      
      // Should deny insurance_number
      expect(result.insurance_number).toBeUndefined();
    });

    it('should evaluate policy for nurse role', () => {
      const result = client.evaluate(resource, 'nurse', 'treatment');
      
      // Should allow these fields
      expect(result.name).toBe(resource.name);
      expect(result.diagnosis).toBe(resource.diagnosis);
      expect(result.medications).toEqual(resource.medications);
      
      // Should mask insurance_number
      expect(result.insurance_number).toBe(MASKED);
    });

    it('should evaluate policy for doctor role with wildcard allow', () => {
      const result = client.evaluate(resource, 'doctor', 'treatment');
      
      // Doctor should get all fields (wildcard allow)
      expect(result).toEqual(resource);
    });

    it('should evaluate policy with conditions', () => {
      // Should fail condition check (active_shift_only: false)
      const resultWithFailedCondition = client.evaluate(
        resource, 
        'receptionist', 
        'treatment', 
        { active_shift_only: false }
      );
      
      // Should return empty object when conditions fail
      expect(Object.keys(resultWithFailedCondition).length).toBe(0);
      
      // Should pass condition check
      const resultWithPassedCondition = client.evaluate(
        resource, 
        'receptionist', 
        'treatment', 
        { active_shift_only: true }
      );
      
      // Should have expected fields when conditions pass
      expect(resultWithPassedCondition.name).toBe(resource.name);
      expect(resultWithPassedCondition.dob).toBe(resource.dob);
    });

    it('should add expiry metadata when justification is provided', () => {
      // Use billing_admin which has justification_ttl defined
      const result = client.evaluate(
        resource, 
        'billing_admin', 
        'billing', 
        { justification: 'Monthly billing reconciliation' }
      );
      
      // Should include metadata with expiry
      expect(result._meta).toBeDefined();
      expect(result._meta.expires_at).toBeDefined();
      
      // Expiry should be in the future
      const expiryDate = new Date(result._meta.expires_at);
      const now = new Date();
      expect(expiryDate > now).toBe(true);
    });

    it('should return empty object for non-existent policy', () => {
      const result = client.evaluate(resource, 'nonexistent-role', 'nonexistent-intent');
      expect(Object.keys(result).length).toBe(0);
    });
  });

  describe('batchEvaluate', () => {
    it('should evaluate multiple resources', () => {
      const resources = [
        resource,
        { ...resource, name: 'John Doe' },
        { ...resource, diagnosis: 'Hypertension' }
      ];
      
      const results = client.batchEvaluate(resources, 'nurse', 'treatment');
      
      // Should return an array of the same length
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBe(resources.length);
      
      // Each result should be processed according to policy
      results.forEach((result, index) => {
        expect(result.name).toBe(resources[index].name);
        expect(result.diagnosis).toBe(resources[index].diagnosis);
        expect(result.insurance_number).toBe(MASKED);
      });
    });
  });
});
const path = require('path');
const fs = require('fs');
const { ApiClient } = require('../hipaah');

// Path to test fixtures
const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const POLICY_PATH = path.join(FIXTURES_DIR, 'sample_policy.yaml');
const RESOURCE_PATH = path.join(FIXTURES_DIR, 'sample_resource.json');

// Mock fetch globally
global.fetch = jest.fn();

describe('ApiClient', () => {
  let client;
  let resource;
  
  beforeEach(() => {
    // Reset mock between tests
    global.fetch.mockReset();
    
    // Create a new client
    client = new ApiClient('https://api.example.com/hipaah', 'test-api-key', POLICY_PATH);
    
    // Load the test resource
    resource = JSON.parse(fs.readFileSync(RESOURCE_PATH, 'utf8'));
  });
  
  describe('constructor', () => {
    it('should create an ApiClient instance', () => {
      expect(client).toBeInstanceOf(ApiClient);
    });
    
    it('should set API URL correctly, adding trailing slash if needed', () => {
      const client1 = new ApiClient('https://api.example.com/hipaah');
      expect(client1.apiUrl).toBe('https://api.example.com/hipaah/');
      
      const client2 = new ApiClient('https://api.example.com/hipaah/');
      expect(client2.apiUrl).toBe('https://api.example.com/hipaah/');
    });
    
    it('should use API key from environment if not provided', () => {
      const originalEnv = process.env.HIPAAH_API_KEY;
      process.env.HIPAAH_API_KEY = 'env-api-key';
      
      const client = new ApiClient('https://api.example.com/hipaah');
      expect(client.apiKey).toBe('env-api-key');
      
      // Restore original env
      process.env.HIPAAH_API_KEY = originalEnv;
    });
  });
  
  describe('remoteEvaluate', () => {
    it('should make API request with correct parameters', async () => {
      // Setup mock response
      const mockResponse = {
        name: 'Lisa Chang',
        diagnosis: '***'
      };
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });
      
      // Call the method
      const result = await client.remoteEvaluate(
        resource, 
        'nurse', 
        'treatment', 
        { department: 'cardiology' }
      );
      
      // Verify correct fetch call
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/hipaah/evaluate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-api-key',
            'X-HIPAAH-CLIENT': 'js-sdk'
          },
          body: JSON.stringify({
            role: 'nurse',
            intent: 'treatment',
            attributes: { department: 'cardiology' },
            resource
          })
        }
      );
      
      // Verify result
      expect(result).toEqual(mockResponse);
    });
    
    it('should handle API errors', async () => {
      // Setup mock error response
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        text: async () => 'Forbidden'
      });
      
      // Verify local fallback is called (spy on evaluate)
      const evaluateSpy = jest.spyOn(client, 'evaluate');
      
      // Call the method
      await client.remoteEvaluate(resource, 'nurse', 'treatment');
      
      // Verify fetch was called
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Verify fallback to local evaluation
      expect(evaluateSpy).toHaveBeenCalledTimes(1);
    });
    
    it('should handle network errors', async () => {
      // Setup mock network error
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      
      // Verify local fallback is called (spy on evaluate)
      const evaluateSpy = jest.spyOn(client, 'evaluate');
      
      // Call the method
      await client.remoteEvaluate(resource, 'nurse', 'treatment');
      
      // Verify fetch was called
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Verify fallback to local evaluation
      expect(evaluateSpy).toHaveBeenCalledTimes(1);
    });
    
    it('should throw error if no fallback policies are available', async () => {
      // Create client without fallback policies
      const clientWithoutPolicies = new ApiClient('https://api.example.com/hipaah');
      
      // Setup mock error response
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      
      // Call should throw
      await expect(
        clientWithoutPolicies.remoteEvaluate(resource, 'nurse', 'treatment')
      ).rejects.toThrow('no local policies are loaded for fallback');
    });
  });
  
  describe('logAccess', () => {
    it('should log access to API', async () => {
      // Setup mock response
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, log_id: '123456' })
      });
      
      // Call the method
      const result = await client.logAccess(
        'doctor',
        'treatment',
        'patient-123',
        'Follow-up visit'
      );
      
      // Verify correct fetch call
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/hipaah/log',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-api-key',
            'X-HIPAAH-CLIENT': 'js-sdk'
          },
          body: expect.stringContaining('"role":"doctor"')
        }
      );
      
      // Verify result
      expect(result).toEqual({ success: true, log_id: '123456' });
    });
    
    it('should handle API errors gracefully', async () => {
      // Setup mock error response
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });
      
      // Call the method
      const result = await client.logAccess(
        'doctor',
        'treatment',
        'patient-123'
      );
      
      // Verify fetch was called
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Should return null on error
      expect(result).toBeNull();
    });
    
    it('should handle network errors gracefully', async () => {
      // Setup mock network error
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the method
      const result = await client.logAccess(
        'doctor',
        'treatment',
        'patient-123'
      );
      
      // Verify fetch was called
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Should return null on error
      expect(result).toBeNull();
    });
  });
});
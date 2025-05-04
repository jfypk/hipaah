declare module 'hipaah' {
  /**
   * Resource object interface
   */
  export interface Resource {
    [key: string]: any;
  }

  /**
   * Policy request interface
   */
  export interface PolicyRequest {
    role: string;
    intent: string;
    attributes: Record<string, any>;
    resource: Resource;
  }

  /**
   * Main client class for the HIPAAH SDK
   */
  export class HipaahClient {
    /**
     * Create a new HipaahClient instance
     * @param policyPath - Optional path to a policy YAML file
     */
    constructor(policyPath?: string);

    /**
     * Load policies from a YAML file
     * @param policyPath - Path to the policy file
     * @returns The loaded policies
     */
    loadPolicy(policyPath: string): Record<string, any>;

    /**
     * Evaluate a resource against the loaded policies
     * @param resource - The resource to evaluate
     * @param role - The user role
     * @param intent - The access intent
     * @param attributes - Optional attributes for policy evaluation
     * @returns The result of policy evaluation
     */
    evaluate(
      resource: Resource,
      role: string,
      intent: string,
      attributes?: Record<string, any>
    ): Resource;

    /**
     * Evaluate multiple resources against the loaded policies
     * @param resources - The resources to evaluate
     * @param role - The user role
     * @param intent - The access intent
     * @param attributes - Optional attributes for policy evaluation
     * @returns The results of policy evaluation
     */
    batchEvaluate(
      resources: Resource[],
      role: string,
      intent: string,
      attributes?: Record<string, any>
    ): Resource[];
  }

  /**
   * Client for interacting with the HIPAAH API
   */
  export class ApiClient extends HipaahClient {
    /**
     * Create a new ApiClient instance
     * @param apiUrl - URL of the HIPAAH API
     * @param apiKey - Optional API key for authentication
     * @param policyPath - Optional path to a policy file for local evaluation
     */
    constructor(apiUrl: string, apiKey?: string, policyPath?: string);

    /**
     * Evaluate a resource against the remote API
     * @param resource - The resource to evaluate
     * @param role - The user role
     * @param intent - The access intent
     * @param attributes - Optional attributes for policy evaluation
     * @returns Promise resolving to the result of policy evaluation
     */
    remoteEvaluate(
      resource: Resource,
      role: string,
      intent: string,
      attributes?: Record<string, any>
    ): Promise<Resource>;
  }

  /**
   * Logger that safely masks sensitive fields
   */
  export class SafeLogger {
    /**
     * Create a new SafeLogger instance
     * @param maskedFields - Array of field names to mask
     */
    constructor(maskedFields?: string[]);

    /**
     * Log an info message
     * @param message - The message to log
     * @param data - Optional data to include in the log
     */
    info(message: string, data?: any): void;

    /**
     * Log a warning message
     * @param message - The message to log
     * @param data - Optional data to include in the log
     */
    warning(message: string, data?: any): void;

    /**
     * Log an error message
     * @param message - The message to log
     * @param data - Optional data to include in the log
     */
    error(message: string, data?: any): void;
  }

  /**
   * Load a resource from a JSON file
   * @param filePath - Path to the JSON file
   * @returns The loaded resource
   */
  export function loadResourceFromFile(filePath: string): Resource;

  /**
   * Save a resource to a JSON file
   * @param resource - The resource to save
   * @param filePath - Path to save the JSON file
   */
  export function saveResourceToFile(resource: Resource, filePath: string): void;

  /**
   * Mask PHI fields in data
   * @param data - The data containing PHI fields
   * @param fieldsToMask - List of field names to mask
   * @returns A copy of the data with PHI fields masked
   */
  export function maskPhiFields(data: any, fieldsToMask: string[]): any;

  /**
   * Merge multiple policy files into one
   * @param policyFiles - List of policy file paths
   * @returns A merged policy object
   */
  export function mergePolicies(policyFiles: string[]): Record<string, any>;
}
/**
 * Masks sensitive fields in data
 * @param {Object|Array} data - The data to mask
 * @param {Array<string>} fieldsToMask - Fields to mask
 * @returns {Object|Array} Masked copy of the data
 */
function maskData(data, fieldsToMask) {
  if (!data || !fieldsToMask || fieldsToMask.length === 0) {
    return data;
  }

  // Handle arrays by recursively processing each item
  if (Array.isArray(data)) {
    return data.map(item => maskData(item, fieldsToMask));
  }

  // Handle non-objects
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  // Create a deep copy of the data
  const maskedData = JSON.parse(JSON.stringify(data));

  // Process each field in the data
  for (const key in maskedData) {
    if (Object.prototype.hasOwnProperty.call(maskedData, key)) {
      // If this field should be masked
      if (fieldsToMask.includes(key)) {
        // Replace with asterisks
        maskedData[key] = '***';
      } 
      // If this is a nested object or array, recurse
      else if (typeof maskedData[key] === 'object' && maskedData[key] !== null) {
        maskedData[key] = maskData(maskedData[key], fieldsToMask);
      }
    }
  }

  return maskedData;
}

/**
 * Deep merges two objects
 * @param {Object} target - Target object to merge into
 * @param {Object} source - Source object to merge from
 * @returns {Object} The merged object
 */
function deepMerge(target, source) {
  const result = { ...target };
  
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
        // If property exists in target and is an object, merge recursively
        if (typeof result[key] === 'object' && result[key] !== null && !Array.isArray(result[key])) {
          result[key] = deepMerge(result[key], source[key]);
        } else {
          // Otherwise just copy the source property
          result[key] = { ...source[key] };
        }
      } else {
        // For non-objects (including arrays), just copy the value
        result[key] = source[key];
      }
    }
  }
  
  return result;
}

/**
 * Validates a resource against a schema
 * @param {Object} resource - The resource to validate
 * @param {Object} schema - The schema to validate against
 * @returns {Object} Validation result with isValid flag and errors
 */
function validateResource(resource, schema) {
  // This is a simple placeholder implementation
  // In a real application, you would use a proper JSON schema validator
  
  const result = {
    isValid: true,
    errors: []
  };
  
  // Check required fields
  if (schema.required) {
    for (const field of schema.required) {
      if (!(field in resource)) {
        result.isValid = false;
        result.errors.push(`Missing required field: ${field}`);
      }
    }
  }
  
  // Check field types
  if (schema.properties) {
    for (const field in schema.properties) {
      if (field in resource) {
        const expectedType = schema.properties[field].type;
        let actualType = typeof resource[field];
        
        // Special handling for arrays
        if (Array.isArray(resource[field])) {
          actualType = 'array';
        }
        
        if (expectedType && actualType !== expectedType) {
          result.isValid = false;
          result.errors.push(`Invalid type for field ${field}. Expected ${expectedType}, got ${actualType}`);
        }
      }
    }
  }
  
  return result;
}

module.exports = {
  maskData,
  deepMerge,
  validateResource
};